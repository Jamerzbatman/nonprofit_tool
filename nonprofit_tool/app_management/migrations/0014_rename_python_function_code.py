# Generated by Django 5.1 on 2024-09-06 22:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_management', '0013_remove_function_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='function',
            old_name='python',
            new_name='code',
        ),
    ]
