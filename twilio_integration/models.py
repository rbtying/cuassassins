from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User

# Create your models here.
import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generates a random string of length size """
    import random
    return ''.join(random.choice(chars) for x in range(size))

class PhoneNumber(models.Model):
    """ Class to keep track of phone numbers """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    phone_number = models.CharField(max_length=32, blank=True)
    is_verified = models.BooleanField(default=False)
    verify_code = models.CharField(max_length=10, blank=True, default="")

    def generate_code(self, commit=True):
        """ Generates a random code """
        self.verify_code = id_generator()

        if commit:
            self.save()

@receiver(post_save, sender=User)
def createPhoneNumber(sender, instance, created, **kwargs):
    if created:
        p = PhoneNumber(user=instance)
        p.phone_number = ''
        p.is_verified = False
        p.generate_code(commit=True)

@receiver(pre_delete, sender=User)
def deletePhoneNumber(sender, instance, **kwargs):
    try:
        if not instance.phonenumber is None:
            instance.phonenumber.delete()
    except:
        pass

import signal_handlers_text
