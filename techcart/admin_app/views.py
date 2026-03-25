from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

# Role checks
def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

# Authentication Views
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin' or request.user.is_superuser:
            return redirect('dashboard')
        else:
            # User is logged in but is a customer, logout or redirect
            logout(request)

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=u, password=p)

        if user is not None:
            if user.role == 'admin' or user.is_superuser:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0) # Session expires when closing browser
                messages.success(request, 'Welcome to the Admin Dashboard.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Access denied. You do not have admin privileges.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_app/login.html')

def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out of the admin panel.')
    return redirect('admin_login')

from customer_app.models import Category, Product, User, Order, OrderItem, ContactMessage

# Dashboard View
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def dashboard(request):
    from django.db.models import Sum
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_customers': User.objects.filter(role='user').count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': Order.objects.filter(status__in=['delivered', 'shipped', 'processing']).aggregate(total=Sum('total_amount'))['total'] or 0,
        'recent_products': Product.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.all()[:5],
    }
    return render(request, 'admin_app/dashboard.html', context)

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        Category.objects.create(name=name, description=description)
        messages.success(request, 'Category added successfully!')
        return redirect('admin_category_list')
    return render(request, 'admin_app/add_category.html')

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_category_list')
    return render(request, 'admin_app/edit_category.html', {'category': category})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        category = Category.objects.get(id=category_id)
        Product.objects.create(
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description,
            image=image
        )
        messages.success(request, 'Product added successfully!')
        return redirect('admin_product_list')
    return render(request, 'admin_app/add_product.html', {'categories': categories})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = get_object_or_404(Category, id=request.POST.get('category'))
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('admin_product_list')
    return render(request, 'admin_app/edit_product.html', {'product': product, 'categories': categories})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin_app/product_list.html', {'products': products})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_app/category_list.html', {'categories': categories})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('admin_category_list')

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('admin_product_list')


# ============================================================
# ORDER MANAGEMENT
# ============================================================
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_order_list(request):
    status_filter = request.GET.get('status', '')
    orders = Order.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'admin_app/order_list.html', {
        'orders': orders,
        'current_status': status_filter,
    })

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}.')
        return redirect('admin_order_detail', order_id=order.id)
    return render(request, 'admin_app/order_detail.html', {'order': order})


# ============================================================
# CUSTOMER MANAGEMENT
# ============================================================
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_customer_list(request):
    customers = User.objects.filter(role='user')
    return render(request, 'admin_app/customer_list.html', {'customers': customers})


# ============================================================
# CONTACT MESSAGES
# ============================================================
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_messages(request):
    contact_messages = ContactMessage.objects.all()
    return render(request, 'admin_app/messages.html', {'contact_messages': contact_messages})

@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_message_detail(request, message_id):
    msg = get_object_or_404(ContactMessage, id=message_id)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'admin_app/message_detail.html', {'msg': msg})
