#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AffiliationAVC04ViewSet

router = DefaultRouter()
router.register(
    r"affiliationsavc04", AffiliationAVC04ViewSet, basename="affiliationavc04"
)

urlpatterns = [
    path("upload/", AffiliationAVC04ViewSet.as_view(), name="document-upload"),
]
