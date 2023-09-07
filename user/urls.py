from rest_framework.routers import DefaultRouter

from user.views import UserViewSet

router = DefaultRouter(trailing_slash=False)

router.register(r"", UserViewSet, basename="users")


urlpatterns = router.urls
