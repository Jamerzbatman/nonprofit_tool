from django.db import models




class Email(models.Model):
    name = models.CharField(max_length=255)
    numbers = models.IntegerField()

    def __str__(self):
        return f'{self.name}'
