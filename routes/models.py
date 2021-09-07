from django.db import models

class Driver(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Visit(models.Model):
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE)
    member = models.CharField(max_length=15)