from django.db import models
from django.contrib.auth.models import User
from .logic import pluck_variables

class Words(models.Model):
    created = models.DateTimeField(auto_now=True)
    words = models.TextField()

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        return self.words[:25] + "..." if len(self.words) > 28 else self.words

    @property
    def fill_fields(self):
        return pluck_variables(self.words)


class Broadcast(Words):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Reply(Words):
    pass
