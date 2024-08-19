# Generated by Django 5.1 on 2024-08-14 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_rename_image_page_placeholder_image_1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='placeholder_image_1',
        ),
        migrations.RemoveField(
            model_name='page',
            name='placeholder_text_1',
        ),
        migrations.AddField(
            model_name='page',
            name='placeholders',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='template_name',
            field=models.CharField(max_length=255),
        ),
    ]
