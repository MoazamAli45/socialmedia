from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like, Post

@receiver(post_save, sender=Like)
def increment_like_count(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.like_count = post.likes.count()
        post.save()

@receiver(post_delete, sender=Like)
def decrement_like_count(sender, instance, **kwargs):
    post = instance.post
    post.like_count = post.likes.count()
    post.save()