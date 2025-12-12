#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.apps import AppConfig


class Affiliationavc09Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "affiliationavc09"

    def ready(self):
        import affiliationavc09.signals
