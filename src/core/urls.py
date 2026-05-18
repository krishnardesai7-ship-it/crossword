from django.conf import settings
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve as media_serve
from django.views.generic import RedirectView
from accounts import views as account_views


urlpatterns = [
    path('accounts/login/', account_views.accounts_login_page, name='accounts_login'),
    path('accounts/register/', account_views.accounts_register, name='accounts_register'),
    path('accounts/login_face/', account_views.accounts_login, name='accounts_login_face'),
    path('accounts/logout/', account_views.accounts_logout, name='accounts_logout'),
    path('accounts/verify-otp/', account_views.verify_otp, name='accounts_verify_otp'),
    path('', include('myapp.urls')),
    path('admin/', admin.site.urls),
    
    
    # path('', RedirectView.as_view(url="/myapp/")),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

]

urlpatterns += [
    path(
        f"{settings.STATIC_URL.lstrip('/')}<path:path>",
        staticfiles_serve,
        {"insecure": True},
    ),
    path(
        f"{settings.MEDIA_URL.lstrip('/')}<path:path>",
        media_serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
