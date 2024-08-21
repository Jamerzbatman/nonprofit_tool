from django.db import models


class emails(models.Model):
    user_name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.user_name}'


class asdfasgaergagr(models.Model):
    date_field = models.DateField()

    def __str__(self):
        return f'{self.date_field}'


class afsadfaggager(models.Model):
    boolean_field = models.BooleanField(default=False)
    date_field = models.DateField()

    def __str__(self):
        return f'{self.boolean_field}'


class fdhshsfghshsdfsrefa(models.Model):
    image_field = models.ImageField(upload_to="images/")
    float_field = models.FloatField()
    integer_field = models.IntegerField()

    def __str__(self):
        return f'{self.image_field}'
