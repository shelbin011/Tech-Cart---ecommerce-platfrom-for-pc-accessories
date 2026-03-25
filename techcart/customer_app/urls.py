from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Profile & Wishlist
    path('profile/', views.profile, name='profile'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Pages
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    
    # Auth URLs
    path('login/', views.customer_login, name='customer_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.customer_logout, name='customer_logout'),
]
