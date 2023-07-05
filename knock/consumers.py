# -*- coding: utf-8 -*-
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from knock.models import KnockChat, KnockChatMessage


class ChatRoomConsumer(JsonWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.chat_pk = None
        self.group_name = None
        self.chat = None

    def connect(self):
        self.chat_pk = self.scope['url_route']['kwargs']['chat_pk']
        self.group_name = f'chat_{self.chat_pk}'
        self.chat = KnockChat.objects.get(pk=self.chat_pk)

        user = self.scope['user']

        if user.pk in [self.chat.knock.requester.pk, self.chat.user.pk]:
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()
        else:
            self.close()

    def disconnect(self, _code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive_json(self, content, **kwargs):
        message = content['message']

        user_pk = self.scope['user'].pk

        if user_pk == self.chat.knock.requester.pk:
            receiver = self.chat.user
        elif user_pk == self.chat.user.pk:
            receiver = self.chat.knock.requester
        else:
            return

        msg = KnockChatMessage()

        msg.chat = self.chat
        msg.sender = self.scope['user']
        msg.receiver = receiver
        msg.text = message
        msg.save()

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chatbox_message',
                'message': f'{ msg.text }',
                'sender': f'{ msg.sender }',
            },
        )

    def chatbox_message(self, event):
        self.send_json(
            {
                'message': event['message'],
                'sender': event['sender'],
            }
        )
