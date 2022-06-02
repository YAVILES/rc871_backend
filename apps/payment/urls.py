from rest_framework import routers

from .views import BankViewSet, PaymentViewSet

router = routers.SimpleRouter()
router.register(r'bank', BankViewSet)
router.register(r'payment', PaymentViewSet)

urlpatterns = [
]

urlpatterns += router.urls
