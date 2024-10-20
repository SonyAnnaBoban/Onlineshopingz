from django.urls import path
from . import views
app_name="Adminapp"
urlpatterns = [
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('adminlogin', views.admin_signin, name='admin_signin'),
    path('users/', views.list_users, name='list_users'),
    path('block-unblock/<int:user_id>/', views.block_unblock_user, name='block_unblock_user'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.soft_delete_category, name='soft_delete_category'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/delete/<int:product_id>/', views.soft_delete_product, name='soft_delete_product'),
    path('categories/', views.list_categories, name='category_list'),  # Added category list
    path('products/', views.list_products, name='product_list'),  # Added product list
]
