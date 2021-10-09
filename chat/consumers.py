import json

from channels.auth import login
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from constance.admin import config
from constance.backends.database.models import Constance
from django.core.exceptions import ObjectDoesNotExist

from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        ''' Cliente se conecta '''
        # Recoge el nombre de la sala
        prefix_app = await self.get_prefix_app()
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = prefix_app + "_%s" % self.room_name
        # Se une a la sala
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Informa al cliente del éxito
        await self.accept()

    async def disconnect(self, close_code):
        ''' Cliente se desconecta '''
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        ''' Cliente envía información y nosotros la recibimos '''
        prefix_app = await self.get_prefix_app()
        text_data_json = json.loads(text_data)
        # login the user to this session.
        await login(self.scope, self.scope['user'])
        # save the session (if the session backend does not access the db you can use `sync_to_async`)
        await database_sync_to_async(self.scope["session"].save)()
        user_id = text_data_json["user_id"]
        text = text_data_json["text"]
        writing = text_data_json["writing"]

        if not writing:
            await self.create_message(text)

        writing = text_data_json["writing"]

        if not writing:
            await self.create_message(text)
            await self.notify(text)

        # Enviamos el mensaje a la sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "user_id": user_id,
                "text": text,
                "writing": writing,
            },
        )

    async def smart_message(self, event):
        ''' Recibimos información de la sala '''
        await self.send(
            text_data=json.dumps(
                event['text']
            )
        )

    async def chat_message(self, event):
        ''' Recibimos información de la sala '''
        user = self.scope['user']
        user_id = str(user.id)
        text = event["text"]
        writing = event["writing"]
        user_name = user.full_name
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "user_id": user_id,
                    "user_name": user_name,
                    "text": text,
                    "room": self.room_group_name,
                    "writing": writing
                }
            )
        )

    def get_room(self):
        staff_only = True if self.room_group_name == 'chat_admin' else False
        room, _ = Room.objects.get_or_create(title=self.room_group_name.replace('chat_', ''), staff_only=staff_only)
        return room

    @database_sync_to_async
    def create_message(self, text: str):
        user = self.scope['user']
        room = self.get_room()
        room.messages.add(Message.objects.create(type='chat_message', user_id=user.id, text=text))

    @database_sync_to_async
    def get_prefix_app(self):
        try:
            prefix_app = Constance.objects.get(key="PREFIX_APP").value
        except ObjectDoesNotExist:
            getattr(config, "PREFIX_APP")
            prefix_app = Constance.objects.get(key="PREFIX_APP").value
        return prefix_app
