from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Products
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='admin_product_list'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),

    # Categories
    path('add-category/', views.add_category, name='add_category'),
    path('categories/', views.category_list, name='admin_category_list'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),

    # Orders
    path('orders/', views.admin_order_list, name='admin_order_list'),
    path('order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),

    # Customers
    path('customers/', views.admin_customer_list, name='admin_customer_list'),

    # Messages
    path('messages/', views.admin_messages, name='admin_messages'),
    path('message/<int:message_id>/', views.admin_message_detail, name='admin_message_detail'),
]