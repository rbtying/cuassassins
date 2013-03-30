# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from assassins_manager.models import *
from assassins_manager.services import render_with_metadata, get_game
from assassins_manager.kill.forms import *
from twilio_integration.models import *
from twilio_integration.services import send_text
from django_facebook import api
from django.views.decorators.csrf import csrf_exempt

def process_contract(game, contract, corpse): 
    print ('processing contract\n')

    """ Processes a kill involving a contract """
    if corpse.squad == contract.target:
        killed = contract.target
        killer = contract.holder
        forward = True
    elif corpse.squad == contract.holder:
        killed = contract.holder
        killer = contract.target
        forward = False

    # just in case
    corpse.set_life(False, True)

    # check if the squad is dead
    dead = True
    for member in killed.members():
        if member.alive:
            dead = False

    # Only refresh the disavowed deadline if the contract was fulfilled normally
    # ie holder -> target
    if forward:
        print('forward\n')
        members = killer.members()
        for member in members:
            print('processing member %s\n' % member.user.username)
            if member.alive and member.role == AssassinType.DISAVOWED and not member.frozen:
                member.set_role(AssassinType.REGULAR, commit=False)
            member.refresh_deadline(commit=False) # calls save internally
            member.save()

    if dead:
        # set the killed squad to REALLY_DEAD
        killed.set_life(False, True)

        if forward:
            # set contract to complete
            contract.set_status(ContractStatus.COMPLETE)
            # transfer contracts over
            killed.transfer_contracts(killer)
        else:
            # we have a problem - there is nobody targetting {killer}
            # note that the contract is not complete at this point

            # this should find somebody who is targetting killed
            # and give them killer's death contract
            killed.transfer_contracts()

        # check if there is more than one squad left alive
        return game.squad_set.filter(alive=True).count() == 1

    # game doesn't change states if no squads are killed
    return False

def process_kill(request, user, game, killtype, corpse, contract, report):
    """ processes a kill """
    assassin = game.getAssassin(user)

    # just in case
    corpse.set_life(False, True)

    if killtype == ReportType.CONTRACT_KILL:
        game_ended = process_contract(game, contract, corpse)
        if game_ended:
            game.end_game()

    elif killtype == ReportType.SANCTIONED_KILL:
        if assassin.role == AssassinType.REGULAR:
            assassin.add_bonus_time()
            assassin.save()
        if not corpse.squad is None:
            temp = False
            for member in corpse.squad.members():
                if member.alive:
                    temp = True
            if not temp:
                corpse.squad.transfer_contracts()

            corpse.squad.save()

        if not contract is None:
            process_contract(game, contract, corpse)

    elif killtype == ReportType.SELF_DEFENSE:
        if not contract is None:
            game_ended = process_contract(game, contract, corpse)
            if game_ended:
                game.end_game()
        else:
            # this is a policeman killed in self-defense
            corpse.refresh_deadline()
            corpse.save()

    k = KillReport(killer=assassin, corpse=corpse)
    k.killtype = killtype
    k.report = report
    k.game = game
    k.save()
    k.send_signal()

    if request:
        try:
            fb = api.get_persistent_graph(request, access_token=user.columbiauserprofile.access_token)
            if fb:
                url = 'http://assassins.columbiaesc.com' + reverse('assassins_manager.report.views.killreport', args=(game_obj.name, k.id, ))
                result = fb.set('me/cuassassins:made', kill=url)
        except:
            pass
    
    assassin = game.getAssassin(user)

    if not assassin.squad is None:
        assassin.squad.updatekills(commit=True)
        # this will also commit assassin_obj.kills
    else:
        assassin.updatekills(commit=True)

    return k

@csrf_exempt
def text(request):
    """ attempting to kill with text """
    if request.POST:
        return report_kill_text(request, request.POST.get('From')[1:], request.POST.get('Body'))
    return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')

def report_kill_text(request, number, text):
    """ attempting to kill with text """
    if not number:
        return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')
    if not text:
        return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')

    try:
        num = PhoneNumber.objects.get(phone_number=number[1:])
    except PhoneNumber.DoesNotExist:
        try:
            num = PhoneNumber.objects.get(phone_number=number)
        except PhoneNumber.DoesNotExist:
            return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')

    request.user = num.user

    strs = text.split(' ')

    lifecode = strs[0].strip().lower()
    corpses = Assassin.objects.filter(lifecode__iexact=lifecode)

    for corpse in corpses:
        data = {
                'corpse': corpse.id,
                'lifecode': lifecode,
                'report': ' '.join(strs[1:]),
            }
        game = corpse.game
        assassin = game.getAssassin(request.user)

        if assassin:
            form = KillForm(data, assassin=assassin)
            if form.is_valid():
                killtype = form.cleaned_data.get('type')
                corpse = form.cleaned_data.get('corpse')
                report = form.cleaned_data.get('report')
                contract = form.cleaned_data.get('contract')

                k = process_kill(request, request.user, game, killtype, corpse, contract, report)
                send_text(number, '[CU Assassins] Kill confirmed')
                return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')
    send_text(number, '[CU Assassins] Kill denied')
    return HttpResponse('<?xml version="1.0" encoding="UTF-8" ?><Response></Response>')

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def report_kill(request, game):
    """ View for reporting kills """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    if request.method == 'POST':
        form = KillForm(request.POST, assassin=assassin_obj)
        if form.is_valid():
            killtype = form.cleaned_data.get('type')
            corpse = form.cleaned_data.get('corpse')
            report = form.cleaned_data.get('report')
            contract = form.cleaned_data.get('contract')

            k = process_kill(request, request.user, game_obj, killtype, corpse, contract, report)

            return HttpResponseRedirect(reverse('assassins_manager.report.views.killreport', args=(game, k.id,)))
    else:
        form = KillForm(assassin=assassin_obj)

    return render_with_metadata(request, 'form.html', game, {
        'form': form,
        'formname': 'Report a Corpse',
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def report_kill_admin(request, game):
    game_obj = get_game(game)
    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None or not assassin_obj.is_admin:
        raise Http404

    if request.method == 'POST':
        form = AdminKillForm(request.POST, game=game_obj)
        if form.is_valid():
            killtype = form.cleaned_data.get('type')
            user = form.cleaned_data.get('killer').user
            corpse = form.cleaned_data.get('corpse')
            report = form.cleaned_data.get('report')
            contract = form.cleaned_data.get('contract')

            k = process_kill(None, user, game_obj, killtype, corpse, contract, report)

            return HttpResponseRedirect(reverse('assassins_manager.report.views.killreport', args=(game, k.id,)))
    else:
        form = AdminKillForm(game=game_obj)

    return render_with_metadata(request, 'form.html', game, {
        'form': form,
        'formname': 'Report a Kill',
        })
