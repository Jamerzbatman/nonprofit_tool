from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class WebSite(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name='websites')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check if we're updating an existing function
        if self.pk:
            original = WebSite.objects.get(pk=self.pk)
            # Ensure the original name, description, or tags have changed
            if (original.name != self.name or
                original.description != self.description or
                set(original.tags.all()) != set(self.tags.all())):
                
                # Create the new WebSiteVersion with the updated details
                new_version = WebSiteVersion.objects.create(
                    website=self,
                    name=self.name,  # Use the current name
                    description=self.description,  # Use the current description
                    version=original.versions.count() + 1
                )
                
                # Copy over the tags from the WebSite to the WebSiteVersion
                new_version.tags.set(self.tags.all())
                
        super().save(*args, **kwargs)


class WebSiteVersion(models.Model):
    website = models.ForeignKey(WebSite, related_name='versions', on_delete=models.CASCADE)
    version = models.IntegerField()
    name = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)

    class Meta:
        unique_together = ('website', 'version')
        ordering = ['-version']

    def save(self, *args, **kwargs):
        if not self.version:
            # Automatically set the version number
            max_version = WebSiteVersion.objects.filter(website_id=self.website_id).aggregate(models.Max('version'))['version__max'] or 0
            self.version = max_version + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.website.name} - v{self.version}'

class App(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(Tag)
    website_relation = models.ManyToManyField('WebSite', related_name='apps', blank=True)
    is_global = models.BooleanField(default=False)  # Field to indicate if the app is available for all websites
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_for_all_websites(self):
        """
        Checks if the app is global (i.e., available for all websites).
        """
        return self.is_global or not self.website_relation.exists()
    
class Packages(models.Model):
    name = models.CharField(max_length=255)
    code =  models.TextField(blank=True, null=True)
    cmd = models.TextField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    function_relation = models.ManyToManyField('Function', related_name='packages', blank=True)
    modeles_relation = models.ManyToManyField('Models', related_name='packages', blank=True)

    def __str__(self):
        return self.name

class Function(models.Model):
    name = models.CharField(max_length=255)
    python = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    is_global = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    app_relation = models.ForeignKey(App, on_delete=models.CASCADE)
    modeles_relation = models.ManyToManyField('Models', related_name='function', blank=True)
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
                    python=original.python,
                    version=original.versions.count() + 1
                )
        super().save(*args, **kwargs)

class FunctionVersion(models.Model):
    function = models.ForeignKey(Function, related_name='versions', on_delete=models.CASCADE)
    version = models.IntegerField()
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


class Models(models.Model):
    name = models.CharField(max_length=255)
    python = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    app_relation = models.ForeignKey(App, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Log(models.Model):
    message = models.TextField()  # The actual error message
    type = models.CharField(max_length=255)  # Type or category of the error
    traceback = models.TextField(blank=True, null=True)  # Full traceback of the error
    timestamp = models.DateTimeField(auto_now_add=True)  # When the error occurred
    resolved = models.BooleanField(default=False)  # If the error has been resolved
    website_relation = models.ForeignKey(WebSite, on_delete=models.CASCADE)
    app_relation = models.ForeignKey(App, on_delete=models.CASCADE, blank=True, null=True)
    function_relation = models.ForeignKey(Function, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f"{self.type} - {self.message[:50]}"