from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    template_name = models.CharField(max_length=255)
    show_in_navbar = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Placeholder(models.Model):
    page = models.ForeignKey(Page, related_name='placeholders', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    text_value = models.TextField(blank=True, null=True)
    image_value = models.ImageField(upload_to='placeholders/', blank=True, null=True)

    def __str__(self):
        return f"{self.page.title} - {self.name}"
