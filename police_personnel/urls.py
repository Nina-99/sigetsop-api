#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PersonnelViewSet, PersonnelSearchAPIView

router = DefaultRouter()
router.register(r"personnel", PersonnelViewSet, basename="personnel")

urlpatterns = [
    path(
        "personnel/search/", PersonnelSearchAPIView.as_view(), name="personnel-search"
    ),
]
urlpatterns += router.urls
