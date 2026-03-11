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

from customer_app.models import Category, Product, User

# Dashboard View
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_customers': User.objects.filter(role='user').count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
        'recent_products': Product.objects.order_by('-created_at')[:5]
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
        return redirect('add_category')
    return render(request, 'admin_app/add_category.html')

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
