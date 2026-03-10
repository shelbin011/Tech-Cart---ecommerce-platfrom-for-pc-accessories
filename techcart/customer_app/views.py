from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Product, Category
from django.shortcuts import get_object_or_404

# Views
def home(request):
    latest_products = Product.objects.all().order_by('-created_at')[:6]
    return render(request, 'customer_app/home.html', {'latest_products': latest_products})

def product_list(request):
    cat_id = request.GET.get('cat')
    categories = Category.objects.all()
    if cat_id:
        products = Product.objects.filter(category_id=cat_id)
        current_cat = get_object_or_404(Category, id=cat_id)
    else:
        products = Product.objects.all()
        current_cat = None
    
    return render(request, 'customer_app/category.html', {
        'products': products, 
        'categories': categories,
        'current_cat': current_cat
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'customer_app/product_detail.html', {'product': product})
def cart(request):
    return render(request, 'customer_app/cart.html')

def checkout(request):
    return render(request, 'customer_app/checkout.html')

def blog(request):
    return render(request, 'customer_app/blog.html')

def contact(request):
    return render(request, 'customer_app/contact.html')

# Authentication Views
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