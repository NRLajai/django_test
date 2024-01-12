from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)       # default signal
def create_customer_for_new_user(sender, **kwargs):
    if kwargs["created"]:                                   # bool value to check if user created or not
        Customer.objects.create(user=kwargs["instance"])
