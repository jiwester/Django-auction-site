# Generated by Django 2.2.5 on 2019-10-07 13:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0004_auto_20191002_1024'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserProfileInfo',
            new_name='UserProfile',
        ),
    ]
