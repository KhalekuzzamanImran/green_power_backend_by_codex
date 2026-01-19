from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.users.cache import invalidate_user_cache
from apps.users.models import User


@receiver(post_save, sender=User)
def user_saved(sender, instance, **kwargs):
    invalidate_user_cache(instance.id)


@receiver(post_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    invalidate_user_cache(instance.id)
