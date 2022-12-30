from django.urls import path, re_path

from . import views

app_name = "account"

urlpatterns = [
    # User Accounts
    path("signup/", views.signup, name="signup"),
    path("login/", views.signin, name="signin"),
    path("logout/", views.signout, {"next_page": "/"}, name="signout"),
    path("activate_success/", views.activate, name="activate_success"),
    path("profiles/", views.profile_list, name="profile_list"),
    re_path(r"^activate/(?P<activation_key>\w+)/$", views.activate, name="activate"),
    re_path(
        r"^activate/retry/(?P<activation_key>\w+)/$",
        views.activate,
        name="activate_retry",
    ),
    re_path(r"^profile/(?P<username>[-\w]+)$", views.profile, name="profile"),
    re_path(
        r"^profile/(?P<username>[-\w]+)/edit-account$",
        views.account_edit,
        name="account_edit",
    ),
    re_path(
        r"^profile/(?P<username>[-\w]+)/edit-profile$",
        views.profile_edit,
        name="profile_edit",
    ),
    re_path(
        r"^profile/(?P<username>[-\w]+)/edit-settings$",
        views.settings_edit,
        name="user_settings_edit",
    ),
]
