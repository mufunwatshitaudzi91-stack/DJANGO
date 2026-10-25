from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Book, UserProfile


@receiver(post_save, sender=Book)
def book_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"📚 New book added to the library: '{instance.title}'")
    else:
        print(f"📖 Book updated: '{instance.title}'")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Give every new user a profile."""
    if created:
        UserProfile.objects.get_or_create(user=instance)