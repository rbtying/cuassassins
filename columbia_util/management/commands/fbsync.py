from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from optparse import make_option
from columbia_util.models import *
from columbia_util.services import verify_uni
from django_facebook.connect import _update_image

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('-u', '--user', action="store", type="string", dest="username", default=""),
        )

    def handle(self, *args, **options):
        if not options['username'] is "":
            users = get_user_model().objects.filter(username=options['username'])
        else:
            users = get_user_model().objects.all()

        for user in users:
            print "processing user " + str(user)
            if user.columbiauserprofile:
                print "updating user " + str(user)
                profile = user.columbiauserprofile
                url = "https://graph.facebook.com/" + str(profile.facebook_id) + "/picture?type=large&access_token=" + str(profile.access_token) + "&width=480&height=320"
                update = False
                try:
                    update =  _update_image(profile, url)
                except:
                    pass

                if update:
                    profile.save()
                    print str(user) + "'s image updated to " + str(profile.image)
            else:
                print str(user) + " does not have a columbiauserprofile"
