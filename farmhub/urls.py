from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin interface.
    path("admin/", admin.site.urls),

    # Authentication and JWT endpoints.
    path("auth/", include("authentications.urls")),

    # Farm management and operational APIs.
    path("api/", include("api.urls")),
]
