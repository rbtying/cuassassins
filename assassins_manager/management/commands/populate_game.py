from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from optparse import make_option
from assassins_manager.models import *

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('-s', '--size', action="store", type="int", dest="size", default=0),
            make_option('-n', '--name', action="store", type="string", dest="name", default=""),
        )

    def handle(self, *args, **options):
        if options['size'] == 0:
            print('Please provide a squad size with -s')
            return
        if options['name'] == "":
            print('Please provide a game name with -n')

        try:
            game = Game.objects.get(name=options['name'])
            game.delete()
        except Game.DoesNotExist:
            pass

        game = Game(name=options['name'], squadsize=options['size'], disavowed_time=72,
                police_resurrect_time=24)
        game.save()

        users = get_user_model().objects.all() 

        i = 0
        squad = None
        for user in users:
            try:
                assassin = game.assassin_set.get(user=user)
            except Assassin.DoesNotExist:
                assassin = Assassin(user=user)
                assassin.squad = None
                assassin.is_admin = user.is_staff
                assassin.game = game
                assassin.resurrect(commit=False)

            if i % options['size'] == 0:
                squad = Squad(name='squad%d' % (i / options['size']), kills=0, alive=True,
                    game=game, public=True)
                squad.save()

            squad.add_assassin(assassin)
            assassin.save()
            i = i + 1
