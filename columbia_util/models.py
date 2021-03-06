from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.conf import settings
from django_facebook.models import FacebookProfileModel
import services

class ColumbiaUserProfile(FacebookProfileModel):
    """ Class to keep track of Columbia-specific profile needs """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    address = models.CharField(max_length=256, blank=True)
    mailbox = models.CharField(max_length=256, blank=True)
    school = models.CharField(max_length=24, blank=True)

    def ldap_update(self, commit=True):
        ldap = services.search(self.user.username)
        if not ldap == None:
            if not ldap.get('givenName') is None:
                self.user.first_name = ldap.get('givenName')[0]

            if not ldap.get('sn') is None:
                self.user.last_name = ldap.get('sn')[0]

            if not ldap.get('homePostalAddress') is None:
                self.address = ldap.get('homePostalAddress')[0]
            else:
                self.address = ""

            if not ldap.get('postalAddress') is None:
                self.mailbox = ldap.get('postalAddress')[0]
            else:
                self.mailbox = ""

            if not ldap.get('ou') is None:
                self.school = ldap.get('ou')[0]

            if not ldap.get('mail') is None:
                self.user.email = ldap.get('mail')[0]

        if commit:
            self.save()

	def __str__(self):
		return self.user.get_full_name()

	def __unicode__(self):
		return self.user.get_full_name()

@receiver(post_save, sender=User)
def createColumbiaUserProfile(sender, instance, created, **kwargs):
    if created:
        c = ColumbiaUserProfile(user=instance)
        c.ldap_update(commit=True)

@receiver(pre_delete, sender=User)
def deleteColumbiaUserProfile(sender, instance, **kwargs):
    try:
        if not instance.columbiauserprofile is None:
            instance.columbiauserprofile.delete()
    except:
        pass
