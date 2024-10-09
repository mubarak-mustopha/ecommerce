from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import (
    force_bytes,
    force_str,
    DjangoUnicodeDecodeError,
)


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .utils import generate_token


# Create your views here.
def send_activation_email(request, user):
    current_site = f"{request.scheme}://{request.get_host()}"
    print(f"Current site: {current_site}")
    print(f"{request.scheme}//{request.get_host()}")
    email_subject = "Activate your account"
    email_body = render_to_string(
        "accounts/activate.html",
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": generate_token.make_token(user),
        },
    )


def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = CustomUser.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return HttpResponse("Activation successful.")
    else:
        return HttpResponse("Activation failed")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # send activation email
            send_activation_email(request, user)
            return HttpResponse("Signup successful!")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def update_user(request):
    form = CustomUserChangeForm()
    form.fields.pop("password")

    return render(request, "accounts/user_update.html", {"form": form})
