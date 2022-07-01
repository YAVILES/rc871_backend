from rest_framework import routers

from .views import UserViewSet, RoleViewSet, WorkflowViewSet, ClientViewSet

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'role', RoleViewSet)
router.register(r'workflow', WorkflowViewSet)
router.register(r'client', ClientViewSet)

urlpatterns = [
]

urlpatterns += router.urls
