from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework import routers

from apps.system.views import ConfigurationViewSet, PeriodicTaskViewSet, IntervalScheduleViewSet, \
    TaskResultViewSet

router = routers.SimpleRouter()
router.register(r'configuration', ConfigurationViewSet)
router.register(r'devices', FCMDeviceAuthorizedViewSet)
router.register(r'task', PeriodicTaskViewSet)
router.register(r'interval_schedule', IntervalScheduleViewSet)
router.register(r'task_results', TaskResultViewSet)

urlpatterns = [
]

urlpatterns += router.urls
