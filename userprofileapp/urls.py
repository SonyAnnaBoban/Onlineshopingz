from django.urls import path
from . import views
app_name = 'userprofileapp'
urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('manage_addresses/', views.manage_addresses, name='manage_addresses'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('profile/user_orders/', views.user_orders, name='user_orders'),
    path('profile/cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
