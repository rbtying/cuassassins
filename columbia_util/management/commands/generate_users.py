from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from optparse import make_option
from columbia_util.models import *
from columbia_util.services import verify_uni

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('-f', '--filename', action="store", type="string", dest="filename", default=""),
        )

    def handle(self, *args, **options):
        if not options['filename'] is "":
            with open(options['filename']) as f:
                content = f.readlines()
                for line in content:
                    username = line.strip().lower()
                    if verify_uni(username):
                        try:
                            u = get_user_model().objects.get(username=username)
                            print('User %s already exists, setting password' % username)
                            u.set_password('1234')
                        except get_user_model().DoesNotExist:
                            print('Creating user %s with password 1234' % username)
                            now = timezone.now()
                            user = get_user_model().objects.create(username=username, is_staff=False, is_active=True, is_superuser=False, last_login=now)
                            user.set_password('1234')
                            user.save()
        else:
            print('Please supply a username file')
