from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
# from twilio.rest import Client
from core.env import config

from .forms import UserCreationForm
from .detection import FaceRecognition
from django.urls import reverse

import random
import socket
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.core import signing
from myapp.models import register as RegisterUser

User = get_user_model()
faceRecognition = FaceRecognition()
FACE_LIB_SETUP_MSG = (
    "Face login is not available on this hosted website. Please log in with your email and password."
)
FACE_NOT_DETECTED_MSG = "Face not detected. Please center your face and try again."


def sync_register_user(user):
    """
    Sync accounts.NewUser data into the legacy myapp.register model
    used by cart, orders, and wishlist. Uses update_or_create so that
    existing records are kept up-to-date, not just created once.
    """
    if not user.email:
        return
    try:
        # Map NewUser gender choices to myapp.register gender choices
        gender_map = {'MALE': 'Male', 'FEMALE': 'Female'}
        gender_value = gender_map.get((user.gender or '').upper(), '')

        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        RegisterUser.objects.update_or_create(
            email=user.email,
            defaults={
                'username': user.username,
                'password': user.password,
                'confirm_password': user.password,
                'gender': gender_value,
                'phone': user.phone_number or '',
                'address': user.country or '',
                's_name': full_name,
            }
        )
    except Exception as e:
        print(f"[sync_register_user] Failed to sync user {user.email}: {e}")


def keep_session_until_logout(request):
    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
    request.session.modified = True


def set_remember_login_cookie(response, user):
    token = signing.dumps(
        user.email,
        key=settings.REMEMBER_LOGIN_SECRET,
        salt=settings.REMEMBER_LOGIN_SALT,
    )
    response.set_cookie(
        settings.REMEMBER_LOGIN_COOKIE_NAME,
        token,
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
    )
    return response


def delete_remember_login_cookie(response):
    response.delete_cookie(
        settings.REMEMBER_LOGIN_COOKIE_NAME,
        secure=not settings.DEBUG,
        samesite='Lax',
    )
    return response


def clear_stale_face_login_messages(request):
    """Keep face-login failures from appearing on the registration form."""
    storage = get_messages(request)
    remaining_messages = [
        message for message in storage
        if str(message) != FACE_NOT_DETECTED_MSG
    ]

    for message in remaining_messages:
        messages.add_message(
            request,
            message.level,
            str(message),
            extra_tags=message.extra_tags,
        )


def accounts_home(request):
    context = {}
    return render(request, "customerapp/home.html", context)


def accounts_register(request):
    form = UserCreationForm(request.POST or None, request.FILES or None, request_user=request.user)

    if form.is_valid():
        try:
            new_user = form.save(commit=False)
            new_user.is_active = False   # 🔴 Verify first
            try:
                new_user.save()
            except IntegrityError as exc:
                error_text = str(exc).lower()
                if "username" in error_text:
                    form.add_error("username", "This username is already taken.")
                elif "email" in error_text:
                    form.add_error("email", "An account with this email already exists.")
                else:
                    form.add_error(
                        None,
                        "Could not create account due to duplicate data. Please try different values.",
                    )
                return render(request, "accounts/register.html", {"form": form, "is_admin_creator": request.user.is_authenticated and request.user.is_staff})

            # Send OTP to user's email and redirect to verification
            otp = send_otp(new_user.email)
            request.session['otp'] = otp
            request.session['user_id'] = new_user.id

            messages.success(
                request,
                f"Account created successfully! {new_user.email}. (Your OTP: {otp})",
            )
            return redirect("accounts:verify_otp")
        except Exception as e:
            messages.error(request, f"Server Error during registration: {str(e)}")
            return render(request, "accounts/register.html", {"form": form})

    ctx = {"form": form, "is_admin_creator": request.user.is_authenticated and request.user.is_staff}
    return render(request, "accounts/register.html", ctx)


def face_enroll_view(request):
    """Browser-based face enrollment using the webcam via JavaScript."""
    user_id = request.session.get('enroll_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("accounts:register")

    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            b64_image = data.get("image", "")
        except Exception:
            b64_image = request.POST.get("image", "")

        if not b64_image:
            from django.http import JsonResponse
            return JsonResponse({"success": False, "message": "No image received."})

        success, message = faceRecognition.enroll_face_from_image(user_id, b64_image)

        from django.http import JsonResponse
        if success:
            # Clear session key — enrollment done
            request.session.pop('enroll_user_id', None)
            return JsonResponse({"success": True, "message": message, "redirect": "/accounts/login/"})
        else:
            return JsonResponse({"success": False, "message": message})

    return render(request, "accounts/face_enroll.html", {"user_id": user_id})



def accounts_login(request):
    if request.method != "POST":
        return redirect("accounts:login")

    import json
    from django.http import JsonResponse
    try:
        data = json.loads(request.body)
        b64_image = data.get("image", "")
    except Exception:
        b64_image = request.POST.get("image", "")

    if not b64_image:
        return JsonResponse({"success": False, "message": "No image received."})

    try:
        face_id, reason = faceRecognition.recognize_face_from_image(b64_image)

        if face_id is None:
            if reason == "no_known_faces":
                return JsonResponse({"success": False, "message": "No registered face data found. Please sign up first."})
            elif reason == "face_library_missing":
                return JsonResponse({"success": False, "message": FACE_LIB_SETUP_MSG})
            elif reason == "face_not_matched":
                return JsonResponse({"success": False, "message": "Face detected but it did not match any active account."})
            elif reason == "no_face_detected":
                return JsonResponse({"success": False, "message": FACE_NOT_DETECTED_MSG})
            else:
                return JsonResponse({"success": False, "message": f"Verification failed: {reason}"})

        user = User.objects.filter(id=face_id, is_active=True).first()

        if user:
            login(request, user)
            keep_session_until_logout(request)
            if user.email:
                request.session["email"] = user.email
                sync_register_user(user)
            response = JsonResponse({"success": True, "message": "Successfully logged in!", "redirect": "/"})
            return set_remember_login_cookie(response, user)
        else:
            return JsonResponse({"success": False, "message": "Face matched but user is inactive or not found."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Login failed: {str(e)}"})

def accounts_logout(request):
    request.session.pop("email", None)
    logout(request)
    response = redirect("accounts:login")
    return delete_remember_login_cookie(response)


def accounts_login_page(request):
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        user = authenticate(request, username=email, password=password)
        if user is None:
            inactive_user = User.objects.filter(email__iexact=email).first()
            if inactive_user and inactive_user.check_password(password) and not inactive_user.is_active:
                messages.error(request, "Please verify your email OTP before logging in.")
            else:
                messages.error(request, "Invalid email or password.")
            return render(request, "accounts/login.html", {"email": email})

        login(request, user)
        keep_session_until_logout(request)
        request.session["email"] = user.email
        sync_register_user(user)
        response = redirect("/")  # Redirect to home page (root URL)
        return set_remember_login_cookie(response, user)

    return render(request, "accounts/login.html")


import threading

def send_otp(email):
    otp = random.randint(100000, 999999)

    print("\n" + "="*50)
    print(f"OTP GENERATED FOR {email}: {otp}")
    print("="*50 + "\n")

    def _send_email_bg():
        # Force IPv4 to prevent IPv6 hanging
        old_getaddrinfo = socket.getaddrinfo
        def new_getaddrinfo(*args, **kwargs):
            responses = old_getaddrinfo(*args, **kwargs)
            return [response for response in responses if response[0] == socket.AF_INET]
        socket.getaddrinfo = new_getaddrinfo

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
        finally:
            socket.getaddrinfo = old_getaddrinfo

    # Run in background thread to avoid Render 30s timeout (500 Error)
    thread = threading.Thread(target=_send_email_bg)
    thread.daemon = True
    thread.start()

    return otp


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        user_id = request.session.get('user_id')

        if str(user_otp) == str(session_otp):
            user = User.objects.get(id=user_id)
            user.is_active = True   # ✅ Activate account
            user.save()

            # Synchronize with myapp.register model
            sync_register_user(user)

            # Store user_id in session so face_enroll knows who to enroll
            request.session['enroll_user_id'] = user.id

            messages.success(request, "Account verified successfully! Please register your face to enable Face Login.")
            return redirect("accounts:face_enroll")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "accounts/verify_otp.html")


def resend_otp(request):
    user_id = request.session.get('user_id')

    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("accounts:register")

    user = User.objects.get(id=user_id)

    # Send to email
    otp = send_otp(user.email)

    request.session['otp'] = otp

    messages.success(request, f"New OTP sent to your email. (Your OTP: {otp})")

    return redirect("accounts:verify_otp")
