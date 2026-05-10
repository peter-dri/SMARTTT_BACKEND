from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
	path("me/", UserViewSet.as_view({"get": "me", "put": "me", "patch": "me"}), name="me"),
	path("", include(router.urls)),
]
