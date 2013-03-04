from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from models import *
from signals import *
import signal_handlers_email

@receiver(assassin_life_signal)
def assassin_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when assassins send life signals """
    pass
    # print("LIFE: %s: %d %s" % (sender.user.username, changed, sender.status_string()))

@receiver(assassin_role_signal)
def assassin_role_signal_handler(sender, changed, role, **kwargs):
    """ signal handler to alert when assassins send role signals """
    pass
    # print("ROLE: %s: %d %d" % (sender.user.username, changed, role))

@receiver(squad_life_signal)
def squad_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when squads send life signals """
    pass
    # print("LIFE: %s: %d %d" % (sender.name, changed, status))

@receiver(squad_member_signal)
def squad_member_signal_handler(sender, change, member, **kwargs):
    """ signal handler to alert when squads gain/lose members """
    pass
    # print("MEMBER: %s: %d %s" % (sender.name, change, member.user.username))

@receiver(game_signal)
def game_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the game state changes """
    pass
    # print("GAME: %s %s" % (sender.name, sender.status_string()))

@receiver(contract_status_signal)
def contract_status_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the contract status changes """
    pass
    # print("CONTRACT: %d %d [%s -> %s]" % (changed, status, sender.holder.name, sender.target.name))

@receiver(kill_signal)
def kill_signal_handler(sender, **kwargs):
    pass
    # print("REPORT: %s > %s : %s" % (sender.killer.user.username, sender.corpse.user.username, sender.report))

