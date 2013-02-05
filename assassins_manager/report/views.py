# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from assassins_manager.models import Assassin, Squad, Contract, Game, GameStatus, KillReport
from assassins_manager.services import render_with_metadata, get_game

def killreports(request, game, reports=None, page_length=25):
    """ Shows kill reports """
    game_obj = get_game(game)

    if reports is None:
        reports = KillReport.objects.filter(game=game_obj)

    page = request.GET.get('page')

    paginator = Paginator(reports.order_by('-date'), page_length)

    try:
        r_list = paginator.page(page)
    except PageNotAnInteger:
        r_list = paginator.page(1)
    except EmptyPage:
        r_list = paginator.page(paginator.num_pages)

    return render_with_metadata(request, 'report/list.html', game, {
        'reports': r_list,
        })

def killreport(request, game, report):
    """ Shows a given kill report """
    game_obj = get_game(game)

    try:
        report = KillReport.objects.get(game=game_obj, id=report)
    except KillReport.DoesNotExist:
        raise Http404
    return render_with_metadata(request, 'report/detail.html', game, {
        'report': report,
        })

def playerkills(request, game, username):
    """ Shows kills made by a given player """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassinByUsername(username)
    return killreports(request, game, assassin_obj.killreports())

def playerdeaths(request, game, username):
    """ Shows kills made by a given player """
    game_obj = get_game(game)

    assassin_obj = game_obj.getAssassinByUsername(username)
    return killreports(request, game, assassin_obj.deathreports())

