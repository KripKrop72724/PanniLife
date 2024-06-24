from django.urls import path
from rest_framework.routers import DefaultRouter
from BaseModules.viewsets import CustomerViewSet

app_name = "BaseModules"
router = DefaultRouter()
router.register(r'donor', CustomerViewSet, basename='donor')

urlpatterns = []
# Append the router URLs
urlpatterns += router.urls
