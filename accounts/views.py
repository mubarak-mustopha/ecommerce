from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse

from .forms import CustomUserCreationForm, CustomUserChangeForm, LoginForm
from .models import CustomUser
from .utils import email_token_generator, add_guest_data


# Create your views here.
def send_activation_email(request, user):
    current_site = f"{request.scheme}://{request.get_host()}"
    subject = "Activate Your Account"
    body = render_to_string(
        "accounts/activation_email.html",
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "domain": current_site,
            "token": email_token_generator.make_token(user),
        },
    )
    email = EmailMessage(
        subject=subject, body=body, from_email=settings.FROM_EMAIL, to=[user.email]
    )
    email.send()


def resend_activation_email(request):
    email = request.COOKIES.get("activation-email")
    user = CustomUser.objects.filter(email=email)

    if not user.exists():
        messages.error(request, "Not allowed.")
        return redirect(settings.LOGIN_URL)

    user = user.first()
    if user.is_email_verified:
        request.session["activation-email"] = None
        messages.success(request, "Account already verified")
        return redirect(settings.LOGIN_URL)

    send_activation_email(request, user)
    return render(
        request,
        "accounts/activation_email_request.html",
        {
            "detail": "resent",
        },
    )


def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = CustomUser.objects.get(pk=uid)

    except:
        # no user object
        messages.error(request, "You entered an invalid activation link.")
        return redirect(settings.LOGIN_URL)

    if email_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, "Activation successful")
        return redirect(settings.LOGIN_URL)
    else:
        return render(request, "accounts/activation_failed.html", {"user": user})


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # send activation email
            send_activation_email(request, user)
            messages.success(request, "Signup successful!")
            return render(
                request, "accounts/activation_email_request.html", {"detail": "sent"}
            )
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def update_user(request):
    form = CustomUserChangeForm()
    form.fields.pop("password")

    return render(request, "accounts/user_update.html", {"form": form})


def login_user(request):
    form = LoginForm()
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "Invalid credentials were provided.")
            return redirect(settings.LOGIN_URL)

        if not user.is_email_verified:
            send_activation_email(request, user)
            return render(
                request, "accounts/activation_email_request.html", {"detail": "request"}
            )
        else:
            add_guest_data(request, user)
            login(request, user)
            next = request.GET.get("next", "home")
            return redirect(next)

    return render(request, "accounts/login.html", {"form": form})


def logout_user(request):
    logout(request)
    return redirect("home")


def userpage(request):
    context = {}
    return render(request, "accounts/userpage.html", context)


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
