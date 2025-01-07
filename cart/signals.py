from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Documents
import os


@receiver(post_save, sender=Documents)
def create_thumbnail(sender, instance, created, **kwargs):
    if created and instance.pdf:
        instance.create_thumbnail()


@receiver(pre_delete, sender=Documents)
def remove_files(sender, instance, **kwargs):
    if instance.pdf:
        try:
            os.remove(instance.pdf.path)
        except FileNotFoundError:
            pass
    if instance.thumbnail:
        try:
            os.remove(instance.thumbnail.path)
        except FileNotFoundError:
            pass
