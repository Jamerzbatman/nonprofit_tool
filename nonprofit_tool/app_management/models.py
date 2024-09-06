from django.db import models

class App(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.app.name} - {self.payment_type.capitalize()} - ${self.amount}'


class Function(models.Model):
    name = models.CharField(max_length=255)
    packages = models.TextField(blank=True, null=True)
    python = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    app_relation = models.ForeignKey(App, on_delete=models.CASCADE)
    url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check if we're updating an existing function
        if self.pk and self.python:
            original = Function.objects.get(pk=self.pk)
            # Ensure the original python code is not null and has changed
            if original.python is not None and original.python != self.python:
                # Only create a version if it's not the first save and original.python is not null
                FunctionVersion.objects.create(
                    function=self,
                    packages=original.packages,
                    python=original.python,
                    version=original.versions.count() + 1
                )
        super().save(*args, **kwargs)

class FunctionVersion(models.Model):
    function = models.ForeignKey(Function, related_name='versions', on_delete=models.CASCADE)
    version = models.IntegerField()
    packages = models.TextField()
    python = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('function', 'version')
        ordering = ['-version']

    def save(self, *args, **kwargs):
        if not self.version:
            # Automatically set the version number
            max_version = FunctionVersion.objects.filter(function_id=self.function_id).aggregate(models.Max('version'))['version__max'] or 0
            self.version = max_version + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.function.name} - v{self.version}'
    
class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    app_relation = models.ForeignKey(App, on_delete=models.CASCADE)
    function_relation = models.ForeignKey(Function, on_delete=models.CASCADE)
    error_message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.app_name} - {self.function_name} - {self.timestamp}"