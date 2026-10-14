from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book


@receiver(post_save, sender=Book)
def book_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"📚 New book added to the library: '{instance.title}'")
    else:
        print(f"📖 Book updated: '{instance.title}'")