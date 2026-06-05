from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core import signing


class RememberLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._restore_login(request)
        return self.get_response(request)

    def _restore_login(self, request):
        if request.user.is_authenticated:
            if request.user.email and request.session.get("email") != request.user.email:
                request.session["email"] = request.user.email
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            return

        token = request.COOKIES.get(settings.REMEMBER_LOGIN_COOKIE_NAME)
        if not token:
            return

        try:
            email = signing.loads(
                token,
                key=settings.REMEMBER_LOGIN_SECRET,
                salt=settings.REMEMBER_LOGIN_SALT,
                max_age=settings.SESSION_COOKIE_AGE,
            )
        except signing.BadSignature:
            return

        User = get_user_model()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        request.session["email"] = user.email
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
