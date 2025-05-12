
from django.urls import path
from . import views

app_name = 'orderapp'
urlpatterns = [
    path('success/', views.order_success, name='success'),  
    path('place_order/', views.place_order, name='place_order'), 
    path('order-history/', views.order_history, name='order_history'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('userorder/<int:order_id>/', views.userorder_detail, name='userorder_detail'),
    
]
