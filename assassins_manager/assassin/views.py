# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.template.context import RequestContext
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from assassins_manager.models import Assassin, Squad, Contract, Game, GameStatus
from assassins_manager.services import render_with_metadata, get_game
from forms import AssassinEditForm

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def my_details(request, game):
    """ View of logged-in user's details """
    return details(request, game, request.user.username)

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def details(request, game, username):
    """ View of any user's details """
    game_obj = get_game(game)

    try:
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        raise Http404

    assassin_obj = game_obj.getAssassin(user)
    if assassin_obj is None:
        raise Http404

    if not game_obj.getAssassin(request.user) is None:
        squad = game_obj.getAssassin(request.user).squad

    if request.method == 'POST':
        form = AssassinEditForm(request.POST, request.FILES, instance=user.columbiauserprofile)
        if form.is_valid():
            form.save()
    else:
        form = AssassinEditForm(instance=user.columbiauserprofile)

    show_lifecode = user == request.user or (assassin_obj.squad == squad and assassin_obj.squad != None)

    # if user != request.user:
    #    form = None 

    return render_with_metadata(request, 'assassin/details.html', game, {
        'assassin': assassin_obj,
        'show_lifecode': show_lifecode,
        'game_started': game_obj.status != GameStatus.REGISTRATION,
        'form': form,
        })
