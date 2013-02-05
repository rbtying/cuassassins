# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from assassins_manager.models import *
from assassins_manager.services import render_with_metadata, get_game
from assassins_manager.kill.forms import *

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
            if member.alive and member.role == AssassinType.DISAVOWED:
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

            # kill the corpse properly
            corpse.set_life(True)

            if killtype == ReportType.CONTRACT_KILL:
                contract = form.cleaned_data.get('contract')
                game_ended = process_contract(game_obj, contract, corpse)
                if game_ended:
                    game_obj.end_game()

            elif killtype == ReportType.SANCTIONED_KILL:
                if assassin_obj.role == AssassinType.REGULAR:
                    assassin_obj.add_bonus_time()
                    assassin_obj.save()
                if not corpse.squad is None:
                    temp = False
                    for member in corpse.squad.members():
                        if member.alive:
                            temp = True
                    if not temp:
                        squad.transfer_contracts()

                    squad.save()

                contract = form.cleaned_data.get('contract')
                if not contract is None:
                    process_contract(game_obj, contract, corpse)

            elif killtype == ReportType.SELF_DEFENSE:
                contract = form.cleaned_data.get('contract')
                if not contract is None:
                    game_ended = process_contract(game_obj, contract, corpse)
                    if game_ended:
                        game_obj.end_game()
                else:
                    # this is a policeman killed in self-defense
                    corpse.refresh_deadline()
                    corpse.save()

            k = KillReport(killer=assassin_obj, corpse=corpse)
            k.report = form.cleaned_data.get('report')
            k.killtype = killtype
            k.game = game_obj
            k.save()
            k.send_signal()
            
            assassin_obj = game_obj.getAssassin(request.user)

            if not assassin_obj.squad is None:
                assassin_obj.squad.updatekills(commit=True)
                # this will also commit assassin_obj.kills
            else:
                assassin_obj.updatekills(commit=True)

            return HttpResponseRedirect(reverse('assassins_manager.report.views.killreport', args=(game, k.id,)))
    else:
        form = KillForm(assassin=assassin_obj)

    return render_with_metadata(request, 'form.html', game, {
        'form': form,
        'formname': 'Report a Corpse',
        })
