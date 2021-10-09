from django.db import models
import uuid
from django.utils.translation import ugettext_lazy as _
from core.models import ModelBase


class Member(models.Model):
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username.capitalize()


class Message(ModelBase):
    type = models.CharField(max_length=255)
    user = models.ForeignKey('security.User', blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField()

    def str(self):
        return self.text


class Room(ModelBase):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)
    messages = models.ManyToManyField(Message, related_name='groups', through='RoomMessage')

    def str(self):
        return self.title


class RoomMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey('Message', verbose_name=_('message'), on_delete=models.CASCADE)
    room = models.ForeignKey('Room', verbose_name=_('room'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('room message')
        verbose_name_plural = _('room messages')

