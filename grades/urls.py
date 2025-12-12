#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from rest_framework.routers import DefaultRouter

from .views import GradeViewSet

router = DefaultRouter()
router.register(r"grades", GradeViewSet, basename="grades")

urlpatterns = router.urls
