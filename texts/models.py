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

class Log(models.Model):
    created = models.DateTimeField(auto_now=True)
    sender = models.CharField(max_length=11)
    recipient = models.CharField(max_length=11)
    words = models.ForeignKey(Broadcast, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=25)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'SMS sent on {self.created.date()} to {self.recipient}.'


class Received(models.Model):
    from_num = models.CharField(max_length=25)
    content = models.TextField()

    def __str__(self):
        if len(self.content) > 28:
            return self.content[:25] + "..."
        return self.content