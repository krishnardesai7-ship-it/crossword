from django.urls import path

from . import views

app_name = 'accounts'


urlpatterns = [
    
    path('register/', views.accounts_register, name='register'),
    path('login/', views.accounts_login_page, name="login"),
    # path('login/', views.login, name='login')
    path("login_face/", views.accounts_login, name="login_face"),
    path("logout/", views.accounts_logout, name="logout"),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    # path('resend-otp/', views.resend_otp, name='resend_otp'),
]
