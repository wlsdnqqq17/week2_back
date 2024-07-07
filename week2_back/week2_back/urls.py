from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("test_app/", include("test_app.urls")),
    path("admin/", admin.site.urls),
    path("MyAvatar/", include("MyAvatar.urls"))
]