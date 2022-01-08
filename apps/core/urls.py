from rest_framework import routers

from apps.core.views import BannerViewSet, BranchOfficeViewSet

router = routers.SimpleRouter()
router.register(r'banner', BannerViewSet)
router.register(r'branch_office', BranchOfficeViewSet)


urlpatterns = [
]

urlpatterns += router.urls
