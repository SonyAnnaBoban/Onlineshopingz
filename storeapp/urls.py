from django.urls import path
from . import views

app_name = 'storeapp'

urlpatterns = [
    path('', views.product_list, name='product_list'),  # List all products with filtering and sorting
    # path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),  # Product detail by category and slug
    path('search/', views.product_search, name='product_search'),  # Product search
    path('store/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),

]
