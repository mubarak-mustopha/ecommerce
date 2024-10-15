from django.urls import path


from .views import signup, update_user, login, activate_user, resend_activation_email

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("update-user/", update_user, name="update-user"),
    path("login/", login, name="login"),
    path("activate-user/<uidb64>/<token>/", activate_user, name="activate"),
    path(
        "resend-activation-email/",
        resend_activation_email,
        name="resend-activation-email",
    ),
]
