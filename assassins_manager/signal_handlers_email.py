from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from models import *
from signals import *
from django.conf import settings
from django.core.mail import send_mail 

prefix = '[CU Assassins] '

def send(subj, msg, emails):
    """ Helper method to send emails """
    msg += "\n\n-- CU Assassins"
    send_mail(prefix + subj, msg, settings.DEFAULT_FROM_EMAIL, emails)

@receiver(assassin_life_signal)
def assassin_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when assassins send life signals """
    if changed:
        if sender.alive:
            msg = 'You have been brought to life in %s' % sender.game.name
            send('Resurrection', msg, (sender.user.email,))

@receiver(assassin_role_signal)
def assassin_role_signal_handler(sender, changed, role, **kwargs):
    """ signal handler to alert when assassins send role signals """
    if changed:
        if sender.role == AssassinType.POLICE:
            msg = 'You have been made a policeman in %s' % sender.game.name
            send('Police Notice', msg, (sender.user.email,))
        elif sender.role == AssassinType.REGULAR:
            msg = 'You have been reset to regular status in %s' % sender.game.name
            send('Status Notice', msg, (sender.user.email,))
        elif sender.role == AssassinType.DISAVOWED:
            msg = 'You have been disavowed in %s' % sender.game.name
            send('Disavowal Notice', msg, (sender.user.email,))

@receiver(squad_life_signal)
def squad_life_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when squads send life signals """
    if changed:
        if not sender.alive:
            msg = 'Your squad (%s) has been eliminated in %s' % (sender.name, sender.game.name)
            emails = list()
            for member in sender.assassin_set.all():
                emails.append(member.user.email)

            send('Squad Elimination Notice', msg, emails)

@receiver(squad_member_signal)
def squad_member_signal_handler(sender, change, member, **kwargs):
    """ signal handler to alert when squads gain/lose members """
    emails = list()
    for member in sender.members():
        emails.append(member.user.email)

    name = member.user.first_name + ' ' + member.user.last_name

    if change == SquadAction.LEFT:
        msg = '%s left your squad (%s) in %s' % (name , sender.name, sender.game.name)
        send('%s left your squad' % name , msg, emails)
    elif change == SquadAction.JOINED:
        msg = '%s has joined your squad (%s) in %s' % (name, sender.name, sender.game.name)
        send('%s joined your squad' % name, msg, emails)

@receiver(game_signal)
def game_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the game state changes """
    emails = list()
    for member in sender.players():
        emails.append(member.user.email)

    if changed:
        if sender.status == GameStatus.IN_PROGRESS:
            msg = '%s has begun! Look for your targets and eliminate them!' % sender.name
            send('Game %s has started' % sender.name, msg, emails)
        elif sender.status == GameStatus.COMPLETE:
            msg= '%s has ended. Contact the game administrator for awards.' % sender.name
            send('Game %s has ended' % sender.name, msg, emails)

@receiver(contract_status_signal)
def contract_status_signal_handler(sender, changed, status, **kwargs):
    """ signal handler to alert when the contract status changes """
    if changed:
        if sender.status == ContractStatus.COMPLETE:
            msg = 'Contract number %s has been completed -- %s has been eliminated. Check for new contracts and targets online!' % (sender.id, sender.target.name)
            emails = list()
            for member in sender.holder.members():
                emails.append(member.user.email)

            send('Contract complete', msg, emails)

@receiver(kill_signal)
def kill_signal_handler(sender, **kwargs):
    if sender.corpse.role == AssassinType.POLICE:
        msg = 'You have been incapacitated by ' + sender.killer.first_name + ' ' + sender.killer.last_name + '. You will be resurrected at ' + sender.corpse.deadline + '.'
    else:
        msg = 'You have been killed by %s. Better luck next time!' % sender.killer.nickname

    msg += "\nThe kill report: " + sender.report
        
    send('Kill Report', msg, (sender.corpse.user.email,))
