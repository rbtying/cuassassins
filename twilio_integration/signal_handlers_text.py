from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from models import *
from assassins_manager.signals import *
from assassins_manager.models import *
from services import send_text
from django.conf import settings

prefix = '[CU Assassins] '

def send(user, msg):
    """ Helper method to send texts """
    number = find_number(user)
    if not number is None:
        send_text(number, prefix + msg, False)

def find_number(assassin):
    """ Finds the number of a user or None """
    try:
        p = PhoneNumber.objects.get(user=assassin.user)
    except PhoneNumber.DoesNotExist:
        return None
    if p is None:
        return None
    elif not p.is_verified:
        return None
    return p.phone_number

@receiver(assassin_life_signal)
def assassin_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when assassins send life signals """
    if changed:
        if sender.alive:
            msg = 'You have been brought to life in %s' % sender.game.name
        send(sender, msg)

@receiver(assassin_role_signal)
def assassin_role_signal_handler(sender, changed, role, **kwargs):
    """ signal handler to alert when assassins send role signals """
    if changed:
        if sender.role == AssassinType.POLICE:
            msg = 'You have been made a policeman in %s' % sender.game.name
        elif sender.role == AssassinType.REGULAR:
            msg = 'You have been reset to regular status in %s' % sender.game.name
        elif sender.role == AssassinType.DISAVOWED:
            msg = 'You have been disavowed in %s' % sender.game.name
        send(sender, msg)

@receiver(squad_life_signal)
def squad_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when squads send life signals """
    if changed:
        if not sender.alive:
            msg = 'Your squad (%s) has been eliminated in %s' % (sender.name, sender.game.name)
            for member in sender.members():
                send(member, msg)


@receiver(squad_member_signal)
def squad_member_signal_handler(sender, change, member, **kwargs):
    """ signal handler to alert when squads gain/lose members """
    name = member.user.first_name + ' ' + member.user.last_name

    if change == SquadAction.LEFT:
        msg = '%s left your squad (%s) in %s' % (name , sender.name, sender.game.name)
    elif change == SquadAction.JOINED:
        msg = '%s has joined your squad (%s) in %s' % (name, sender.name, sender.game.name)

    for member in sender.members():
        send(member, msg)

@receiver(game_signal)
def game_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the game state changes """
    if changed:
        if sender.status == GameStatus.IN_PROGRESS:
            msg = '%s has begun! Look for your targets and eliminate them!' % sender.name
        elif sender.status == GameStatus.COMPLETE:
            msg= '%s has ended. Contact the game administrator for awards.' % sender.name

    for member in sender.players():
        send(member, msg)

@receiver(contract_status_signal)
def contract_status_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the contract status changes """
    if changed:
        if sender.status == ContractStatus.COMPLETE:
            msg = 'Contract number %s has been completed -- %s has been eliminated. Check for new contracts and targets online!' % (sender.id, sender.target.name)
            for member in sender.holder.members():
                send(member, msg)

@receiver(kill_signal)
def kill_signal_handler(sender, **kwargs):
    if sender.corpse.role == AssassinType.Police:
        msg = 'You have been incapacitated by ' + sender.killer.first_name + ' ' + sender.killer.last_name + '. You will be resurrected at ' + sender.corpse.deadline + '.'
    else:
        msg = 'You have been killed by %s. Better luck next time!'

    msg += "\nThe kill report: " + sender.report

    send(sender.corpse.user, msg)
