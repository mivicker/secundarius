from django.db import models
from django.contrib.auth.models import User


class Words(models.Model):
    created = models.DateTimeField(auto_now=True)
    words = models.TextField()

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        if len(self.words) > 28:
            return self.words[:25] + "..."
        return self.words


class Broadcast(Words):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Reply(Words):
    pass
