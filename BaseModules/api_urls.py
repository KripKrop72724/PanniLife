from django.urls import path
from rest_framework.routers import DefaultRouter
from BaseModules.viewsets import CustomerViewSet, CustomerViewSetProtected

app_name = "BaseModules"
router = DefaultRouter()
router.register(r'donor', CustomerViewSet, basename='donor')
router.register(r'donor_protected', CustomerViewSetProtected, basename='donor_protected')


urlpatterns = []
# Append the router URLs
urlpatterns += router.urls
