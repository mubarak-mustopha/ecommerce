from django.urls import path


from .views import signup, update_user

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("update-user/", update_user, name="update-user"),
]
