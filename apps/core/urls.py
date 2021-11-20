from rest_framework import routers

from apps.core.views import BannerViewSet

router = routers.SimpleRouter()
router.register(r'banner', BannerViewSet)

urlpatterns = [
]

urlpatterns += router.urls
