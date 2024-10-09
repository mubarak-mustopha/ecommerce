from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes, force_str, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .utils import email_token_generator


# Create your views here.
def send_activation_email(request, user):
    current_site = f"{request.scheme}://{request.get_host()}"
    subject = "Activate Your Account"
    body = render_to_string(
        "accounts/activate.html",
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "domain": current_site,
            "token": email_token_generator.make_token(user),
        },
    )


def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = CustomUser.objects.get(pk=uid)

    except:
        user = None

    if user and email_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return HttpResponse("Activation successful")

    return HttpResponse("Activation failed. Pls request another activation link.")


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
