from rest_framework import routers

from apps.core.views import BannerViewSet, BranchOfficeViewSet, UseViewSet, PlanViewSet, CoverageViewSet, \
    PremiumViewSet, MarkViewSet, ModelViewSet, VehicleViewSet, StateViewSet, CityViewSet, MunicipalityViewSet

router = routers.SimpleRouter()
router.register(r'banner', BannerViewSet)
router.register(r'branch_office', BranchOfficeViewSet)
router.register(r'use', UseViewSet)
router.register(r'plan', PlanViewSet)
router.register(r'coverage', CoverageViewSet)
router.register(r'premium', PremiumViewSet)
router.register(r'mark', MarkViewSet)
router.register(r'model', ModelViewSet)
router.register(r'vehicle', VehicleViewSet)
router.register(r'state', StateViewSet)
router.register(r'city', CityViewSet)
router.register(r'municipality', MunicipalityViewSet)

urlpatterns = [
]

urlpatterns += router.urls
