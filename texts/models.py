from django.db import models

class Words(models.Model):
    created = models.DateTimeField(auto_now=True)
    words = models.TextField()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if len(self.words) > 28:
            return self.words[:25] + "..."
        return self.words

class Log(models.Model):
    created = models.DateTimeField(auto_now=True)
    sender = models.CharField(max_length=11)
    recipient = models.CharField(max_length=11)
    words = models.ForeignKey(Words, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=25)

    def __str__(self):
        return f'SMS sent on {self.created.date()} to {self.recipient}.'

class Received(models.Model):
    from_num = models.CharField(max_length=25)
    content = models.TextField()

    def __str__(self):
        if len(self.words) > 28:
            return self.words[:25] + "..."
        return self.words