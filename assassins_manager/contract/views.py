# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from assassins_manager.models import Assassin, Squad, Contract, Game
from assassins_manager.services import render_with_metadata, get_game
from assassins_manager.game.views import is_admin

@login_required
def details(request, game, contract):
    """ Displays details of any contract """
    game_obj = get_game(game)

    try:
        contract_obj = Contract.objects.get(id=contract, game=game_obj)
    except Contract.DoesNotExist:
        raise Http404

    assassin_obj = game_obj.getAssassin(request.user)
    if assassin_obj is None:
        raise Http404

    access = is_admin(request.user, game_obj) or contract_obj.holder == assassin_obj.squad

    return render_with_metadata(request, 'contract/details.html', game, {
        'contract': contract_obj,
        'access': access
        })
