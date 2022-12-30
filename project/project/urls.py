from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("datacore.urls", namespace="datacore")),
    path("account/", include("account.urls", namespace="account")),
    path("admin/", admin.site.urls, name="admin"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
