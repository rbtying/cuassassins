from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware, make_naive
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from signals import *

# Create your models here.

import string
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generates a random string of length size """
    import random
    return ''.join(random.choice(chars) for x in range(size))

class AssassinType:
    REGULAR = 0
    DISAVOWED = 1
    POLICE = 2
    NOT_IN_GAME = 3

class Assassin(models.Model):
    """ Class to keep track of assassins' pictures, status, and profile """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    picture = models.ImageField(upload_to='assassins/%Y/%m', blank=True)
    alive = models.BooleanField(default=True)
    lifecode = models.CharField(max_length=8, blank=True)
    kills = models.IntegerField(default=0) 
    is_admin = models.BooleanField(default=False)

    nickname = models.CharField(max_length=255, default="John Doe")
    address = models.CharField(max_length=256, default="1234 John Jay Hall")

    deadline = models.DateTimeField(blank=True, null=True)

    role = models.IntegerField(default=AssassinType.NOT_IN_GAME)

    squad = models.ForeignKey('Squad', null=True, blank=True)
    game = models.ForeignKey('Game')

    def __unicode__(self):
        return self.nickname + " (" + self.user.first_name + " " + self.user.last_name + ")"

    def set_life(self, life, commit=True):
        """ Sets the life status of this Assassin """
        changed = self.alive != life
        self.alive = life
        assassin_life_signal.send(sender=self, changed=changed, status=self.alive)

        if commit:
            self.save()

    def set_role(self, role, commit=True):
        changed = self.role != role
        self.role = role
        assassin_role_signal.send(sender=self, changed=changed, role=self.role)
        if commit:
            self.save()

    def in_game(self):
        return self.role != AssassinType.NOT_IN_GAME

    def is_police(self):
        return self.role == AssassinType.POLICE

    def is_disavowed(self):
        return self.role == AssassinType.DISAVOWED

    def resurrect(self, commit=True):
        """ Brings the assassin to life """
        self.set_life(life=True, commit=False)
        self.lifecode = id_generator()
        if commit:
            self.save()

    def updatekills(self, commit=True):
        """ Maintains consistency between kills and reports """
        self.kills = self.killreports().count()
        if self.role == AssassinType.POLICE:
            self.kills = self.kills - self.deathreports().count()
        
        if commit:
            self.save()

    def killreports(self):
        """ gets reports of kills this assassin has made """
        return KillReport.objects.filter(game=self.game, killer=self)

    def deathreports(self):
        """ gets reports of deaths this assassin has experienced. """
        return KillReport.objects.filter(game=self.game, corpse=self)

    def set_deadline(self, deadline, commit=True):
        self.deadline = deadline
        assassin_deadline_signal.send(sender=self, deadline=self.deadline)
        if commit:
            self.save()

    def refresh_deadline(self, soft_reset=False, commit=True):
        """ refreshes the action deadline on each assassin """
        if not self.role == AssassinType.POLICE:
            t = now() + timedelta(hours=self.game.disavowed_time)
            # if not self.deadline is None:
            #     t2 = self.deadline + timedelta(hours=self.game.disavowed_time)
            #     if t2 > t and not soft_reset:
            #         self.set_deadline(t2, commit)
            #     else:
            #         self.set_deadline(t, commit)
            # else: 
            self.set_deadline(t, commit)
        else:
            self.set_deadline(now() + timedelta(hours=self.game.police_resurrect_time), commit)

    def add_bonus_time(self, commit=True):
        if not self.role == AssassinType.POLICE:
            t = now() + timedelta(hours=self.game.disavowed_time)
            if not self.deadline is None:
                t2 = self.deadline + timedelta(hours=self.game.disavowed_time)
                if t2 > t:
                    self.set_deadline(t2, commit)
                else:
                    self.set_deadline(t, commit)
            else:
                self.set_deadline(t, commit)

    def status_string(self):
        """ Gets the status of this Assassin """
        if self.role == AssassinType.REGULAR:
            if self.alive:
                return 'Alive'
            else:
                return 'Dead'
        elif self.role == AssassinType.POLICE:
            if self.alive:
                return 'Police'
            else:
                return 'Police (incapacitated)'
        elif self.role == AssassinType.DISAVOWED:
            if self.alive:
                return 'Disavowed'
            else:
                return 'Dead (disavowed)'

    def clean(self):
        """ Checks to see if this assassin is already in the game """
        duplicates = self.game.assassin_set.filter(user=self.user)
        for duplicate in duplicates:
            if not duplicate == self:
                raise ValidationError('Assassin already in game')

class GameStatus:
    """ Enum to keep track of game status """
    REGISTRATION = 0
    IN_PROGRESS = 1
    COMPLETE = 2

class Game(models.Model):
    """ Model to keep track of individual assassins games """
    name = models.CharField(max_length=255)
    status = models.IntegerField(default=GameStatus.REGISTRATION)
    disavowed_time = models.IntegerField(default=72)
    police_resurrect_time = models.IntegerField(default=24)

    code = models.CharField(max_length=10)

    squadsize = models.IntegerField(default=4)

    def __unicode__(self):
        return self.name

    def players(self):
        """ Gets players in squads """
        return self.assassin_set.exclude(squad=None, role=AssassinType.NOT_IN_GAME) | self.assassin_set.filter(role=AssassinType.POLICE)

    def numPlayers(self):
        """ Number of players """
        return len(self.players())

    def numSquads(self):
        """ Number of squads """
        self.prune_squads()
        return len(self.squad_set.all())

    def getAssassin(self, user):
        """ Gets an assassin associated with user in this game """
        try:
            assassin_obj = self.assassin_set.get(user=user)
        except Assassin.DoesNotExist:
            assassin_obj = None
        return assassin_obj

    def getAssassinByUsername(self, username):
        """ Gets an assassin associated with a username in this game """
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            user = None
        return self.getAssassin(user)

    def status_string(self):
        """ Easier to read version of status """
        if self.status == GameStatus.REGISTRATION:
            return 'Registration'
        elif self.status == GameStatus.IN_PROGRESS:
            return 'In progress'
        elif self.status == GameStatus.COMPLETE:
            return 'Complete'

    def start_game(self):
        """ Starts the game by generating contracts for all of the squads and setting the status """
        changed = not self.status == GameStatus.IN_PROGRESS

        self.reset_game()
        self.status = GameStatus.IN_PROGRESS
        game_signal.send(sender=self, changed=changed, status=self.status)

        prev_squad = None

        squadlist = list(self.squad_set.all())
        import random
        random.shuffle(squadlist)

        for squad in squadlist:
            if squad.assassin_set.exists():
                if not prev_squad is None:
                    self.link(prev_squad, squad)
                prev_squad = squad
        self.link(squadlist[-1], squadlist[0])
        self.save()
       
        player_set = self.players()
        for assassin in player_set.all():
            assassin.refresh_deadline(soft_reset=True)

    def link(self, squad1, squad2):
        """ Links squad1 to squad2 with a contract """
        try:
            contract = Contract.objects.get(game=self, holder=squad1, target=squad2)
        except Contract.DoesNotExist:
            contract = Contract(holder=squad1, target=squad2)
            contract.set_status(ContractStatus.ACTIVE, False)
            contract.game = self
            contract.save()

    def end_game(self):
        """ Ends the game by setting status to complete """
        changed = not self.status == GameStatus.COMPLETE
        self.status = GameStatus.COMPLETE
        game_signal.send(sender=self, changed=changed, status=self.status)
        self.save()

    def reset_game(self):
        """ Resets the game by deleting all contracts and resetting all kills """
        for contract in self.contract_set.all():
            contract.delete()

        for squad in self.squad_set.all():
            squad.kills = 0
            squad.set_life(True, False)
            squad.save()

        for assassin in self.players():
            assassin.resurrect()
            assassin.kills = 0
            if assassin.role == AssassinType.DISAVOWED:
                assassin.set_role(AssassinType.REGULAR)

        for report in self.killreport_set.all():
            report.delete()

        changed = not self.status == GameStatus.REGISTRATION
        self.status = GameStatus.REGISTRATION
        game_signal.send(sender=self, changed=changed, status=self.status)
        self.save()

    def prune_squads(self):
        """ Removes empty squads """
        squads = self.squad_set.all()
        for squad in squads:
            if not squad.assassin_set.exists():
                squad.delete()

    def generateCode(self, commit=True):
        self.code = id_generator()
        if commit:
            self.save()

class SquadAction:
    LEFT = 0
    JOINED = 1

class Squad(models.Model):
    """ Model of Squad which tracks name, status, and kills """
    name = models.CharField(max_length=255)
    alive = models.BooleanField(default=True)
    kills = models.IntegerField(default=0)
    game = models.ForeignKey(Game)
    public = models.BooleanField(default=False)
    code = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name

    def set_life(self, life, commit=True):
        """ sets whether this squad is alive or dead """
        changed = self.alive == life
        self.alive = life
        squad_life_signal.send(sender=self, changed=changed, status=self.alive)
        if commit:
            self.save()

    def add_assassin(self, assassin, commit=True):
        """ Adds an assassin to this squad """
        assassin.squad = self
        # assassin.role = AssassinType.REGULAR
        squad_member_signal.send(sender=self, change=SquadAction.JOINED, member=assassin)
        if commit:
            assassin.save()

    def remove_assassin(self, assassin, commit=True):
        """ Removes an assassin from the squad """
        if assassin.squad == self:
            assassin.squad = None
            # assassin.role = AssassinType.NOT_IN_GAME
            squad_member_signal.send(sender=self, change=SquadAction.LEFT, member=assassin)
            if commit:
                assassin.save()

    def active_contracts(self):
        """ Gets active contracts """
        return Contract.objects.filter(game=self.game, holder=self, status=ContractStatus.ACTIVE)

    def completed_contracts(self):
        """ Gets completed contracts """
        return Contract.objects.filter(game=self.game, holder=self, status=ContractStatus.COMPLETE)

    def updatekills(self, commit=True):
        """ maintains consistency between killcounter and reports in game """
        kills = 0
        for member in self.members():
            member.updatekills(commit=True)
            kills = kills + member.kills
        self.kills = kills
        if commit:
            self.save()

    def members(self):
        return self.assassin_set.all()

    def transfer_contracts(self, other=None):
        """ method to transfer active contracts to other, or to an arbitrary squad targetting self """
        transferable_contracts = Contract.objects.filter(game=self.game, target=self, status=ContractStatus.ACTIVE)
        if other is None:
            if transferable_contracts.exists():
                transfer_to = transferable_contracts[0].holder
            else:
                return
        else:
            transfer_to = other
        contracts_to_transfer = self.active_contracts()
        for c in contracts_to_transfer:
            if c.target != transfer_to:
                c.holder = transfer_to
                c.save()
            else:
                c.delete()
        transfer_to.save()
        self.save()

    def generateCode(self, commit=True):
        self.code = id_generator()
        if commit:
            self.save()

class ContractStatus:
    """ Enum to keep track of various states of contracts """
    ACTIVE = 0
    PENDING = 1
    COMPLETE = 2
    INCOMPLETE = 3
    PENDING_TERMINATED = 4

class Contract(models.Model):
    """ Model for contracts which keeps track of hte holder, target, and status """
    holder = models.ForeignKey(Squad, related_name="holder")
    target = models.ForeignKey(Squad, related_name="target")
    status = models.IntegerField(default=ContractStatus.ACTIVE)
    game = models.ForeignKey(Game)

    def set_status(self, status, commit=True):
        changed = self.status != status
        self.status = status
        contract_status_signal.send(sender=self, changed=changed, status=self.status)
        if commit:
            self.save()

    def clean(self):
        if self.holder == self.target:
            raise ValidationError('Suicide contracts not permitted')

        duplicates = Contract.objects.filter(game=self.game, holder=self.holder, target=self.target)
        for duplicate in duplicates:
            if not duplicate == self:
                raise ValidationError('Duplicate Contract')

    def __unicode__(self):
        return str(self.id) + ": " + self.target.name + " (" + self.status_string() + ")"

    def status_string(self):
        if self.status == ContractStatus.ACTIVE:
            return "Active"
        elif self.status == ContractStatus.PENDING:
            return "Pending"
        elif self.status == ContractStatus.COMPLETE:
            return "Complete"
        elif self.status == ContractStatus.INCOMPLETE:
            return "Incomplete"
        elif self.status == ContractStatus.PENDING_TERMINATED:
            return "Pending (terminated)"

class ReportType:
    CONTRACT_KILL = 0 # killing within contract
    SELF_DEFENSE = 1 # killing the person who is supposed to kill you
    SANCTIONED_KILL = 2 # killing disavowed people

class KillReport(models.Model):
    killer = models.ForeignKey(Assassin, related_name='killreporter')
    corpse = models.ForeignKey(Assassin, related_name='corpse')
    killtype = models.IntegerField()
    report = models.TextField()
    game = models.ForeignKey(Game)
    date = models.DateTimeField(default=datetime.now)
    
    def send_signal(self):
        kill_signal.send(sender=self)

    def type_string(self):
        if self.killtype == ReportType.CONTRACT_KILL:
            return 'Assassination'
        elif self.killtype == ReportType.SELF_DEFENSE:
            return 'Self defense'
        elif self.killtype == ReportType.SANCTIONED_KILL:
            return 'Sanctioned Kill'

@receiver(post_save, sender=Assassin)
def assassin_to_life(sender, instance, created, **kwargs):
    """ signal handler to resurrect Assassins when they are created """
    if created:
        instance.resurrect(commit=False)
        if not instance.squad is None:
            if not instance.squad.game is None:
                instance.game = instance.squad.game
        instance.save()

@receiver(pre_delete, sender=Game)
def game_pre_delete(sender, instance, **kwargs):
    """ signal handler to delete all squads/assassins/contracts related to instance when instance is deleted """
    for squad in instance.squad_set.all():
        squad.delete()
    for assassin in instance.assassin_set.all():
        assassin.delete()
    for contract in instance.contract_set.all():
        contract.delete()
    for report in instance.killreport_set.all():
        report.delete()

@receiver(post_save, sender=Game)
def game_post_save(sender, instance, created, **kwargs):
    """ signal handler which gets rid of empty squads when the game is saved """
    # if created:
    #     instance.generateCode()
    instance.prune_squads()

@receiver(post_save, sender=Squad)
def squad_to_life(sender, instance, created, **kwargs):
    """ signal handler to set code if not set when they are created """
    if created:
        if not instance.code:
            instance.generateCode()

@receiver(pre_delete, sender=Squad)
def squad_pre_delete(sender, instance, **kwargs):
    """ signal handler to maintain game consistency when a squad is deleted """
    instance.transfer_contracts()
    contracts = Contract.objects.filter(game=instance.game, holder=instance) | Contract.objects.filter(game=instance.game, target=instance)
    for contract in contracts:
        contract.delete()
    for assassin in instance.members():
        assassin.squad = None

import signal_handlers
