from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Product, Category, Order, OrderItem, Wishlist, ContactMessage
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal

# ============================================================
# HELPER: Get cart from session
# ============================================================
def _get_cart(request):
    """Return the cart dict from session. Format: {product_id_str: quantity}"""
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def _get_cart_items(request):
    """Return list of dicts with product info + quantity + line total."""
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for pid_str, qty in cart.items():
        try:
            product = Product.objects.get(id=int(pid_str))
            line_total = product.price * qty
            items.append({
                'product': product,
                'quantity': qty,
                'line_total': line_total,
            })
            total += line_total
        except Product.DoesNotExist:
            continue
    return items, total

def _cart_count(request):
    """Total number of items in cart."""
    cart = _get_cart(request)
    return sum(cart.values())


# ============================================================
# VIEWS
# ============================================================
def home(request):
    latest_products = Product.objects.all().order_by('-created_at')[:6]
    categories = Category.objects.all()[:6]
    return render(request, 'customer_app/home.html', {
        'latest_products': latest_products,
        'categories': categories,
        'cart_count': _cart_count(request),
    })

def product_list(request):
    cat_id = request.GET.get('cat')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')
    categories = Category.objects.all()

    products = Product.objects.all()

    if cat_id:
        products = products.filter(category_id=cat_id)
        current_cat = get_object_or_404(Category, id=cat_id)
    else:
        current_cat = None

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    return render(request, 'customer_app/category.html', {
        'products': products,
        'categories': categories,
        'current_cat': current_cat,
        'query': query,
        'sort': sort,
        'cart_count': _cart_count(request),
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'customer_app/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'cart_count': _cart_count(request),
    })


# ============================================================
# CART VIEWS
# ============================================================
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    pid = str(product_id)

    qty = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1

    if pid in cart:
        cart[pid] += qty
    else:
        cart[pid] = qty

    # Cap at stock
    if cart[pid] > product.stock:
        cart[pid] = product.stock

    _save_cart(request, cart)
    messages.success(request, f'"{product.name}" added to cart.')

    # Redirect back to where user came from
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)

def cart(request):
    items, total = _get_cart_items(request)
    shipping = Decimal('0.00') if total >= 2000 else Decimal('99.00')
    grand_total = total + shipping
    return render(request, 'customer_app/cart.html', {
        'cart_items': items,
        'cart_total': total,
        'shipping': shipping,
        'grand_total': grand_total,
        'cart_count': _cart_count(request),
    })

def update_cart(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            product = get_object_or_404(Product, id=product_id)
            cart[pid] = min(qty, product.stock)
        else:
            cart.pop(pid, None)
        _save_cart(request, cart)
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


# ============================================================
# CHECKOUT & ORDERS
# ============================================================
@login_required(login_url='customer_login')
def checkout(request):
    items, total = _get_cart_items(request)
    if not items:
        messages.warning(request, 'Your cart is empty. Add some products first.')
        return redirect('product_list')

    shipping = Decimal('0.00') if total >= 2000 else Decimal('99.00')
    grand_total = total + shipping
    user = request.user

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        zipcode = request.POST.get('zipcode', '').strip()
        phone = request.POST.get('phone', '').strip()
        payment = request.POST.get('payment', 'cod')

        if not all([full_name, email, address, city, zipcode]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'customer_app/checkout.html', {
                'cart_items': items, 'cart_total': total,
                'shipping': shipping, 'grand_total': grand_total,
                'cart_count': _cart_count(request),
            })

        # Create the order
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            address=address,
            city=city,
            zipcode=zipcode,
            phone=phone,
            total_amount=grand_total,
            payment_method=payment,
        )

        # Create order items & reduce stock
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price,
            )
            product = item['product']
            product.stock -= item['quantity']
            if product.stock < 0:
                product.stock = 0
            product.save()

        # Clear cart
        _save_cart(request, {})
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'customer_app/checkout.html', {
        'cart_items': items,
        'cart_total': total,
        'shipping': shipping,
        'grand_total': grand_total,
        'cart_count': _cart_count(request),
    })

@login_required(login_url='customer_login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customer_app/order_confirmation.html', {
        'order': order,
        'cart_count': _cart_count(request),
    })

@login_required(login_url='customer_login')
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'customer_app/order_history.html', {
        'orders': orders,
        'cart_count': _cart_count(request),
    })

@login_required(login_url='customer_login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customer_app/order_detail.html', {
        'order': order,
        'cart_count': _cart_count(request),
    })


# ============================================================
# USER PROFILE
# ============================================================
@login_required(login_url='customer_login')
def profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.address = request.POST.get('address', '').strip()
        user.city = request.POST.get('city', '').strip()
        user.zipcode = request.POST.get('zipcode', '').strip()
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    recent_orders = Order.objects.filter(user=user)[:5]
    return render(request, 'customer_app/profile.html', {
        'user': user,
        'recent_orders': recent_orders,
        'cart_count': _cart_count(request),
    })


# ============================================================
# WISHLIST
# ============================================================
@login_required(login_url='customer_login')
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'customer_app/wishlist.html', {
        'wishlist_items': items,
        'cart_count': _cart_count(request),
    })

@login_required(login_url='customer_login')
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wish, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wish.delete()
        messages.success(request, f'"{product.name}" removed from wishlist.')
    else:
        messages.success(request, f'"{product.name}" added to wishlist.')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


# ============================================================
# SEARCH
# ============================================================
def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'customer_app/search_results.html', {
        'products': products,
        'query': query,
        'cart_count': _cart_count(request),
    })


# ============================================================
# BLOG & CONTACT
# ============================================================
def blog(request):
    return render(request, 'customer_app/blog.html', {
        'cart_count': _cart_count(request),
    })

def contact(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if all([first_name, email, message_text]):
            ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                message=message_text,
            )
            messages.success(request, 'Your message has been sent! We\'ll get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all required fields.')

    return render(request, 'customer_app/contact.html', {
        'cart_count': _cart_count(request),
    })


# ============================================================
# AUTHENTICATION
# ============================================================
def customer_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('dashboard')
        return redirect('home')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=u, password=p)

        if user is not None:
            if user.role == 'admin' or user.is_superuser:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)
                messages.success(request, 'Welcome Admin! Directed to dashboard.')
                return redirect('dashboard')
            else:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0) # Session expires when closing browser
                messages.success(request, 'Successfully logged in.')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'customer_app/login.html')

def customer_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p1 = request.POST.get('password1')
        p2 = request.POST.get('password2')

        if p1 != p2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'customer_app/register.html')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'customer_app/register.html')

        try:
            # Create the customer user with 'user' role
            user = User.objects.create_user(username=u, email=e, password=p1)
            user.role = 'user'
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('customer_login')
        except Exception as ex:
            messages.error(request, f'Error creating account: {str(ex)}')

    return render(request, 'customer_app/register.html')

def customer_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('customer_login')