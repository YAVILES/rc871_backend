from rest_framework import routers

from .views import UserViewSet, RoleViewSet, WorkflowViewSet

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)
router.register(r'role', RoleViewSet)
router.register(r'workflow', WorkflowViewSet)
urlpatterns = [
]

urlpatterns += router.urls
