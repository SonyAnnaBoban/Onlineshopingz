from django.urls import path
from . import views
app_name ='Accountsapp'
urlpatterns = [
    path('', views.home, name='home'),  
    path('register/', views.Register, name='Register'),
    path('login/', views.user_login, name='user_login'),
    path('resend_otp', views.resend_otp, name='resend_otp'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    
    
    

]