# Generated by Django 5.1 on 2024-09-13 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dreamspace', '0009_function_log_function_relation_functionversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='function',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='function',
            name='is_global',
            field=models.BooleanField(default=False),
        ),
    ]
