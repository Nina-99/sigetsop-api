#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SickLeaveViewSet

router = DefaultRouter()
router.register(r"sick-leaves", SickLeaveViewSet, basename="sickleave")

urlpatterns = [
    path("", include(router.urls)),
]
