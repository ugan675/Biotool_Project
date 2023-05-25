from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

from base.templatetags.custom_tags import filename


def get_upload_path(instance, filename):
    return 'documents/{0}/{1}'.format(instance.user.pk, filename)


class File(models.Model):
    file = models.FileField(upload_to=get_upload_path)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    command = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
