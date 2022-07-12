from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers

from recipes.views import FollowViewSet

router = routers.DefaultRouter()
router.register("users", FollowViewSet, basename="follow")

urlpatterns = [
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("docs/", TemplateView.as_view(template_name="redoc.html")),
    path("api/", include("recipes.urls")),
    path("api/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("rest-auth/", include("rest_framework.urls", namespace="auth")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
