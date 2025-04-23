from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def set_role_for_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser and instance.role != 'admin':
        instance.role = 'admin'
        instance.save()
