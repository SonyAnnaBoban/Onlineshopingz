from django.urls import path
from . import views
app_name = 'cartapp'
urlpatterns = [
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_cart/<int:product_id>/<int:quantity>/', views.update_cart_item, name='update_cart_item'),

]
