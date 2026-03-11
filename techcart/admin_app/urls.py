from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='admin_product_list'),
    path('categories/', views.category_list, name='admin_category_list'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
]