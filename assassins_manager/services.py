from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from datetime import datetime
from models import *

def get_game(name):
    """ Gets a game """
    try:
        game_obj = Game.objects.get(name=name)
    except Game.DoesNotExist:
        raise Http404
    return game_obj

def render_with_metadata(request, template_name, gamename='', dictionary={}):
    try:
        game_obj = Game.objects.get(name=gamename)
    except Game.DoesNotExist:
        game_obj = None

    if gamename == '' or game_obj is None:
        if request.session.get('game_name'):
            del request.session['game_name']
    else:
        dictionary['game'] = game_obj
        request.session['game_name'] = gamename

    if request.user.is_authenticated():
        if not game_obj is None:
            try:
                assassin_obj = game_obj.assassin_set.get(user=request.user)
            except Assassin.DoesNotExist:
                assassin_obj = Assassin(user=request.user)
                assassin_obj.squad = None
                assassin_obj.is_admin = False
                assassin_obj.game = game_obj
                assassin_obj.resurrect(commit=False)
                assassin_obj.save()
            game_obj.save()
    return render(request, template_name, dictionary)

def game_cron(request):
    """ method to call to disavow players and resurrect police """

    games = Game.objects.filter(status=GameStatus.IN_PROGRESS)

    from django.utils.timezone import now
    now = now()

    for game in games:
        for a in game.players():
            if a.role == AssassinType.REGULAR:
                if a.alive == True and a.deadline and now > a.deadline:
                    a.set_role(AssassinType.DISAVOWED, True)
            elif a.role == AssassinType.POLICE:
                if a.alive == False and now > a.deadline:
                    a.resurrect()
        for s in game.squad_set.all():
            alive = False
            for a in s.members():
                if a.alive:
                    alive = True
            contracts = Contract.objects.filter(game=game, target=s, status=ContractStatus.ACTIVE)
            if not alive:
                for contract in contracts:
                    contract.set_status(ContractStatus.COMPLETE, True)
            elif not contracts:
                contract = Contract(holder=game.squad_set.all()[0], target=s)
                contract.game = game
                contract.save()
            s.alive = alive
            s.save()
    return HttpResponse("done")
