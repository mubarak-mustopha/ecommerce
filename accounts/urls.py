from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("update-user/", views.update_user, name="update-user"),
    path("login/", views.login, name="login"),
    path("activate-user/<uidb64>/<token>/", views.activate_user, name="activate"),
    path(
        "resend-activation-email/",
        views.resend_activation_email,
        name="resend-activation-email",
    ),
    # password reset views
    path(
        "password_reset/",
        views.CustomPassowrdResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        views.CustomPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
