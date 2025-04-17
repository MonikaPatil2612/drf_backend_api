from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.DataFileViewSet)
router.register(r'visualizations', views.VisualizationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]