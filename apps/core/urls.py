from rest_framework import routers

from apps.core.views import BannerViewSet, BranchOfficeViewSet, UseViewSet, PlanViewSet

router = routers.SimpleRouter()
router.register(r'banner', BannerViewSet)
router.register(r'branch_office', BranchOfficeViewSet)
router.register(r'use', UseViewSet)
router.register(r'plan', PlanViewSet)


urlpatterns = [
]

urlpatterns += router.urls
