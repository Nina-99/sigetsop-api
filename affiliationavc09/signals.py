from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import AffiliationAVC09  # Asumo que así se llama tu modelo


@receiver(post_save, sender=AffiliationAVC09)
def notificar_cambio_baja(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()

    person = instance.personnel
    # Lógica de negocio
    tipo_accion = ""
    if instance.state == "ENTREGAR":
        tipo_accion = "nueva_baja"
    elif instance.state == "ENTREGADO":
        tipo_accion = "eliminar_baja"

    if tipo_accion:
        payload = {
            "type": "send_notification",
            "message": {
                "action": tipo_accion,
                "id": instance.id,
                "nombre": f"{person.last_name} {person.maternal_name} {person.first_name}",
                "estado": instance.state,
            },
        }

        async_to_sync(channel_layer.group_send)("bajas_medicas", payload)
