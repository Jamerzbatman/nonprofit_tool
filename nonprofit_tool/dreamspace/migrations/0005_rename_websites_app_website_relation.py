# Generated by Django 5.1 on 2024-09-12 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dreamspace', '0004_alter_websiteversion_tags_app'),
    ]

    operations = [
        migrations.RenameField(
            model_name='app',
            old_name='websites',
            new_name='website_relation',
        ),
    ]
