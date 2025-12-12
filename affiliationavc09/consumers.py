#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

session_data = {}


class UploadLinkConsumer(WebsocketConsumer):
    def connect(self):
        # Genera un ID de sesión único
        self.session_id = str(uuid.uuid4())
        self.session_group_name = f"upload_{self.session_id}"

        # Acepta la conexión ANTES de enviar mensajes o unirse a grupos
        self.accept()

        # Unirse al grupo de la sesión (ahora que el socket está aceptado)
        async_to_sync(self.channel_layer.group_add)(
            self.session_group_name, self.channel_name
        )

        # Envía el ID de sesión al cliente de escritorio
        self.send(
            text_data=json.dumps(
                {
                    "type": "session_created",
                    "session_id": self.session_id,
                }
            )
        )

        print(f"✅ WS conectado. Sesión: {self.session_id}")

    def disconnect(self, close_code):
        # Sale del grupo de sesión
        async_to_sync(self.channel_layer.group_discard)(
            self.session_group_name, self.channel_name
        )

        # Limpia los datos de sesión si existen
        if self.session_id in session_data:
            del session_data[self.session_id]

        print(f"⚠️ WS desconectado. Sesión: {self.session_id} — Código: {close_code}")

    def receive(self, text_data):
        """Maneja mensajes entrantes desde el cliente (opcional)."""
        try:
            data = json.loads(text_data)
            print("📩 Mensaje recibido:", data)
        except json.JSONDecodeError:
            print("❌ Error: mensaje no es JSON válido")

    def image_uploaded(self, event):
        """Recibe mensajes del grupo (por ejemplo, cuando el backend móvil sube una imagen)."""
        self.send(
            text_data=json.dumps(
                {
                    "type": "image_received",
                    "image_url": event["image_url"],
                    "initial_points": event["initial_points"],
                }
            )
        )


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Unimos al usuario al grupo 'bajas_medicas'
        self.group_name = "bajas_medicas"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Este método recibe el mensaje del grupo y lo envía al WebSocket del cliente
    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
