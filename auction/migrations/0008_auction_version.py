# Generated by Django 2.2.5 on 2019-10-29 17:05

from django.db import migrations
import ool


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0007_auto_20191024_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='version',
            field=ool.VersionField(default=0),
        ),
    ]
