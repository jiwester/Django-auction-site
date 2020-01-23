from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django import forms
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=200, default="en")


@receiver(post_save, sender=User)
def profile_for_new_user(instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance).save()

