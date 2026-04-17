"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
 path('', views.home, name='home'),
 path('about/', views.about, name='about'),
 path('contact/', views.contact, name='contact'),
 path('base/', views.base, name='base'),
 path('cart/', views.cart, name='cart'),
 path('search/', views.search, name='search'),
 path('faq/', views.faq, name='faq'),
#  path('register/', views.register, name='register'),
#  path('login/', views.login, name='login'),
 
    path('logout/', views.logout, name='logout'),
    # path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    # path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:id>/', views.product, name='product'),
    path('blog/', views.blog, name='blog'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_to_cart/<int:id>/', views.cart_add, name='add_to_cart'),
    
    path('cart_plus/<int:id>', views.cart_plus, name='cart_plus'),
    path('cart_minus/<int:id>', views.cart_minus, name='cart_minus'),
    path('cart_delete/<int:id>', views.cart_delete, name='cart_delete'),
    path('add_wishlist/<int:id>', views.add_wishlist, name='add_wishlist'),
    path('wishlist_delete/<int:id>', views.wishlist_delete, name='wishlist_delete'),
    path('submit_review/<int:id>/', views.submit_review, name='submit_review'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    path('success/', views.payment_success, name='success'),
    path('profile/', views.profile, name='profile'),
    

]
