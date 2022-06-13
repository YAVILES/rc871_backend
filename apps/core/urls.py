from rest_framework import routers

from apps.core.views import BannerViewSet, BranchOfficeViewSet, UseViewSet, PlanViewSet, CoverageViewSet, \
    PremiumViewSet, MarkViewSet, ModelVehicleViewSet, VehicleViewSet, StateViewSet, CityViewSet, MunicipalityViewSet, \
    PolicyViewSet, HistoricalChangeRateViewSet, HomeDataAPIView, SectionViewSet

router = routers.SimpleRouter()
router.register(r'banner', BannerViewSet)
router.register(r'section', SectionViewSet)
router.register(r'branch_office', BranchOfficeViewSet)
router.register(r'use', UseViewSet)
router.register(r'plan', PlanViewSet)
router.register(r'coverage', CoverageViewSet)
router.register(r'premium', PremiumViewSet)
router.register(r'mark', MarkViewSet)
router.register(r'model', ModelVehicleViewSet)
router.register(r'vehicle', VehicleViewSet)
router.register(r'state', StateViewSet)
router.register(r'city', CityViewSet)
router.register(r'municipality', MunicipalityViewSet)
router.register(r'policy', PolicyViewSet)
router.register(r'rate', HistoricalChangeRateViewSet)
router.register(r'home', HomeDataAPIView, basename='home')

urlpatterns = [
]

urlpatterns += router.urls
