from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
# from twilio.rest import Client
from core.env import config

from .forms import UserCreationForm
from .detection import FaceRecognition
from django.urls import reverse

import random
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

User = get_user_model()
faceRecognition = FaceRecognition()
FACE_LIB_SETUP_MSG = (
    "Face recognition dependencies are not installed for this Python interpreter. "
    "Activate the project virtual environment (`.\\fenv\\Scripts\\activate`) "
    "or install requirements, then try again."
)
FACE_NOT_DETECTED_MSG = "Face not detected. Please center your face and try again."


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
    if request.method == "GET":
        clear_stale_face_login_messages(request)

    form = UserCreationForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.is_active = False   # ðŸ”´ Verify first
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
            return render(request, "accounts/register.html", {"form": form})

        # Capture and store dlib embedding for this user.
        registered, face_message = faceRecognition.enroll_face(new_user.id)
        if not registered:
            new_user.delete()
            if face_message == "face_library_missing":
                messages.error(request, FACE_LIB_SETUP_MSG)
            else:
                messages.error(request, face_message)
            return redirect("accounts:register")

        # Send OTP Email
        email = new_user.email
        otp = send_otp(email)

        # Save in session
        request.session['otp'] = otp
        request.session['user_id'] = new_user.id

        # âœ… ADD MESSAGE HERE
        messages.success(
            request, "OTP sent to your email. Please verify your account.")

        return redirect("accounts:verify_otp")

    return render(request, "accounts/register.html", {"form": form})



def accounts_login(request):
    if request.method != "POST":
        return redirect("accounts:login")

    try:
        face_id, reason = faceRecognition.recognize_face()

        if face_id is None:
            if reason == "no_known_faces":
                messages.error(request, "No registered face data found. Please sign up first.")
                return redirect(reverse("accounts:login") + "?auto_register=1")

            elif reason == "face_library_missing":
                messages.error(request, FACE_LIB_SETUP_MSG)

            elif reason == "camera_error":
                messages.error(request, "Unable to access camera. Check camera permission and try again.")

            elif reason == "face_not_matched":
                messages.error(request, "Face detected but it did not match any active account.")
                return redirect(reverse("accounts:login") + "?auto_register=1")

            elif reason == "canceled":
                messages.error(request, "Face login was canceled.")

            elif reason == "no_face_detected":
                messages.error(request, FACE_NOT_DETECTED_MSG)
                return redirect("accounts:register")

            else:
                messages.error(request, FACE_NOT_DETECTED_MSG)

            return redirect("accounts:login")

        user = User.objects.filter(id=face_id, is_active=True).first()

        if user:
            login(request, user)

            if user.email:
                request.session["email"] = user.email

            # IMPORTANT FIX HERE 👇
            return redirect("home")   # make sure this exists in urls.py

        else:
            messages.error(request, "Face not matched with any active account.")
            return redirect(reverse("accounts:login") + "?auto_register=1")

    except Exception as e:
        messages.error(request, f"Login failed: {str(e)}")
        return redirect("accounts:login")

def accounts_logout(request):
    request.session.pop("email", None)
    logout(request)
    return redirect("accounts:login")


def accounts_login_page(request):
    return render(request, "accounts/login.html")


def send_otp(email):
    otp = random.randint(100000, 999999)

    send_mail(
        'Your OTP Code',
        f'Your OTP is {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return otp


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        user_id = request.session.get('user_id')

        if str(user_otp) == str(session_otp):
            user = User.objects.get(id=user_id)
            user.is_active = True   # âœ… Activate account
            user.save()

            messages.success(request, "Account verified successfully!")
            return redirect("accounts:login")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "accounts/verify_otp.html")


# def resend_otp(request):
#     user_id = request.session.get('user_id')

#     if not user_id:
#         messages.error(request, "Session expired. Please register again.")
#         return redirect("accounts:register")

#     user = User.objects.get(id=user_id)

#     otp = send_otp(user.email)

#     request.session['otp'] = otp

#     messages.success(request, "New OTP sent to your email.")

#     return redirect("accounts:verify_otp")
