import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Rendering, Document, FloorPlan, Lot


@receiver(post_delete, sender=Rendering)
def delete_rendering_file(sender, instance, **kwargs):
    """
    Delete the file from filesystem when a Rendering instance is deleted.
    """
    if instance.image:
        try:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        except (ValueError, OSError):
            # ValueError: if image.path doesn't exist
            # OSError: if file doesn't exist or can't be deleted
            pass


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """
    Delete the file from filesystem when a Document instance is deleted.
    """
    if instance.document:
        try:
            if os.path.isfile(instance.document.path):
                os.remove(instance.document.path)
        except (ValueError, OSError):
            pass


@receiver(post_delete, sender=FloorPlan)
def delete_floor_plan_file(sender, instance, **kwargs):
    """
    Delete the file from filesystem when a FloorPlan instance is deleted.
    """
    if instance.plan_file:
        try:
            if os.path.isfile(instance.plan_file.path):
                os.remove(instance.plan_file.path)
        except (ValueError, OSError):
            pass


@receiver(post_delete, sender=Lot)
def delete_lot_rendering_file(sender, instance, **kwargs):
    """
    Delete the file from filesystem when a Lot instance is deleted.
    """
    if instance.lot_rendering:
        try:
            if os.path.isfile(instance.lot_rendering.path):
                os.remove(instance.lot_rendering.path)
        except (ValueError, OSError):
            pass
