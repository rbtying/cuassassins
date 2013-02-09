# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from assassins_manager.models import *
from assassins_manager.services import render_with_metadata, get_game
from assassins_manager.squad.forms import *
from django_facebook import api

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def add_squad(request, game):
    """ View to add a new squad """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    if request.method == 'POST':
        form = AddForm(request.POST, assassin=assassin_obj)
        if form.is_valid():
            squad = form.save()
            squad.add_assassin(assassin_obj, commit=True)
            fb = api.get_persistent_graph(request, access_token=request.user.columbiauserprofile.access_token)
            if fb:
                url = 'http://assassins.columbiaesc.com' + reverse('assassins_manager.squad.views.details', args=(game_obj.name, squad.id, ))
                result = fb.set('me/cuassassins:create', squad=url)
            return HttpResponseRedirect(reverse('assassins_manager.squad.views.details', args=(game, squad.id,)))
    else:
        form = AddForm(assassin=assassin_obj)

    return render_with_metadata(request, 'form.html', game, {
        'formname': 'Create Squad',
        'form': form,
        })

def join_squad(request, game):
    """ View to join a squad """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    if request.method == 'POST':
        form = JoinForm(request.POST, assassin=assassin_obj)
        if form.is_valid():
            squad = form.cleaned_data.get('squad')
            squad.add_assassin(assassin_obj, commit=True)
            fb = api.get_persistent_graph(request, access_token=request.user.columbiauserprofile.access_token)
            if fb:
                url = 'http://assassins.columbiaesc.com' + reverse('assassins_manager.squad.views.details', args=(game_obj.name, squad.id, ))
                result = fb.set('me/cuassassins:join', squad=url)
            return HttpResponseRedirect(reverse('assassins_manager.squad.views.details', args=(game, squad.id,)))
    else:
        form = JoinForm(assassin=assassin_obj)

    return render_with_metadata(request, 'form.html', game, {
        'formname': 'Join Squad',
        'form': form,
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def leave_squad(request, game):
    """ View to leave the current squad """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    if request.method == 'POST':
        form = LeaveForm(request.POST, assassin=assassin_obj)
        if form.is_valid():
            sq = assassin_obj.squad
            sq.remove_assassin(assassin_obj, commit=True)
            if not sq is None:
                if not sq.assassin_set.exists():
                    sq.delete()
            return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))
    else:
        form = LeaveForm(assassin=assassin_obj)
    return render_with_metadata(request, 'form.html', game, {
        'form': form,
        'formname': 'Leave Squad',
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def my_details(request, game):
    """ View to show current squad details """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404
    if assassin_obj.squad is None:
        return HttpResponseRedirect(reverse('assassins_manager.squad.views.join_squad', args=(game,)))
    else:
        return details(request, game, assassin_obj.squad.id)

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def my_contracts(request, game):
    """ View to show current squad contracts """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    squad = assassin_obj.squad
    contracts = Contract.objects.filter(holder=squad).order_by('status')
    return render_with_metadata(request, 'squad/contracts.html', game, {
        'squad': squad,
        'contracts': contracts
        })

# @user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def details(request, game, squad):
    """ View to show squad details """
    game_obj = get_game(game)

    app_id = settings.FACEBOOK_APP_ID

    try:
        squad_obj = game_obj.squad_set.get(id=squad)
    except Squad.DoesNotExist:
        raise Http404

    assassin_obj = None

    if request.user.is_authenticated():
        assassin_obj = game_obj.getAssassin(user=request.user)
    show_code = not assassin_obj is None and assassin_obj.squad == squad_obj

    return render_with_metadata(request, 'squad/details.html', game, {
        'squad': squad_obj,
        'show_code': show_code,
        'app_id': app_id,
        })
