from django.conf import settings
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve as media_serve
from django.views.generic import RedirectView


urlpatterns = [
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
