#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"avc09", views.AffiliationAVC09ViewSet, basename="avc09")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "upload09/",
        views.UploadAndProcessView.as_view(),
        name="ocr_proces",
    ),
    # path("upload/", views.Uplo.as_view(), name="upload"),
    path("process/", views.CorrectAndOcrView.as_view(), name="process-image"),
    path("generate-mobile-token/", views.GenerateMobileTokenView.as_view()),
    path("exchange-mobile-token/", views.ExchangeMobileTokenView.as_view()),
    path("upload/mobile/", views.MobileUploadView.as_view()),
    # path("avc09-save/", views.SaveDocumentView.as_view(), name="save-document"),
]
