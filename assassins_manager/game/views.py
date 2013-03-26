# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from assassins_manager.models import *
from assassins_manager.services import render_with_metadata, get_game
from django_facebook import api

from forms import *

def disavowed(request, game):
    """ Shows all disavowed assassins in the game, sorted by kills """
    game_obj = get_game(game)

    assassins = game_obj.players().filter(role=AssassinType.DISAVOWED).order_by('-alive', '-kills')

    return render_assassins_list(request, game, assassins, 'Disavowed Assassins', 1000)

def police(request, game):
    """ Shows all police in the game """
    game_obj = get_game(game)

    assassins = game_obj.players().filter(role=AssassinType.POLICE).order_by('-kills', '-alive')

    return render_assassins_list(request, game, assassins, 'Police', 1000)

def assassins(request, game, page_length=25):
    """ Shows all assassins in the game, sorted by squad """
    game_obj = get_game(game)

    if request.GET.get('sortby') == 'kills':
        assassins = game_obj.players().order_by('-kills', '-alive', 'role')
        l = 'Assassins by kills'
    else:
        assassins = game_obj.players().order_by('-alive', 'role', '-kills')
        l = 'Assassins by status'

    return render_assassins_list(request, game, assassins, l, page_length)

def render_assassins_list(request, game, assassins, listtitle, page_length=25):
    """ Helper method to paginate assassins list """
    page = request.GET.get('page')

    if request.GET.get('pagelen'):
        page_length = request.GET.get('pagelen')

    paginator = Paginator(assassins, page_length)

    try:
        a_list = paginator.page(page)
    except PageNotAnInteger:
        a_list = paginator.page(1)
    except EmptyPage:
        a_list = paginator.page(paginator.num_pages)

    if request.GET.get('showfbid') == 'yes':
        showfbid = True
    else:
        showfbid = False

    return render_with_metadata(request, 'game/assassins.html', game, {
        'assassins': a_list,
        'listtitle': listtitle,
        'showfbid': showfbid,
        })

def squads(request, game, page_length=25):
    """ Shows all squads in the game, sorted by status and kills """
    game_obj = get_game(game)

    if request.GET.get('sortby') == 'kills':
        squads = game_obj.squad_set.order_by('-kills', '-alive')
        l = 'Squads by kills'
    else:
        squads = game_obj.squad_set.order_by('-alive', '-kills')
        l = 'Squads by ranking'

    page = request.GET.get('page')

    paginator = Paginator(squads, page_length)

    try:
        s_list = paginator.page(page)
    except PageNotAnInteger:
        s_list = paginator.page(1)
    except EmptyPage:
        s_list = paginator.page(paginator.num_pages)


    return render_with_metadata(request, 'game/squads.html', game, {
        'listtitle': l,
        'squads': s_list,
        'squadsize': range(1, game_obj.squadsize + 1),
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def contracts(request, game, page_length=25):
    """ Shows all contracts in the game -- ADMIN ONLY -- """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        contracts = game_obj.contract_set.order_by('status')

        page = request.GET.get('page')

        paginator = Paginator(contracts, page_length)

        try:
            c_list = paginator.page(page)
        except PageNotAnInteger:
            c_list = paginator.page(1)
        except EmptyPage:
            c_list = paginator.page(paginator.num_pages)
        
        return render_with_metadata(request, 'game/contracts.html', game, {
            'contracts': c_list,
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.squad.views.my_contracts', args=(game,)))

def scoreboard(request, game):
    """ Alias for squads list """
    return squads(request, game)

def details(request, game):
    """ Shows general game details """
    game_obj = get_game(game)
    app_id = settings.FACEBOOK_APP_ID

    return render_with_metadata(request, 'game/details.html', game, { 'app_id':
        app_id, })

def gamelist(request, page_length=25):
    """ Shows a list of all games, ordered by status """
    games = Game.objects.all().order_by('status')
    page = request.GET.get('page')

    paginator = Paginator(games, page_length)

    try:
        g_list = paginator.page(page)
    except PageNotAnInteger:
        g_list = paginator.page(1)
    except EmptyPage:
        g_list = paginator.page(paginator.num_pages)

    return render_with_metadata(request, 'game/list.html', '', {
        'games': g_list,
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def create_game(request):
    """ Creates a new game and sets the existing user as the administrator """
    if request.method == 'POST':
        form = AddGameForm(request.POST)
        if form.is_valid():
            game_obj = form.save()
            assassin_obj = Assassin(user=request.user)
            assassin_obj.squad = None
            assassin_obj.is_admin = True
            assassin_obj.game = game_obj
            assassin_obj.resurrect(commit=False)
            assassin_obj.save()

            try:
                fb = api.get_persistent_graph(request, access_token=request.user.columbiauserprofile.access_token)
                if fb:
                    url = 'http://assassins.columbiaesc.com' + reverse('assassins_manager.game.views.details', args=(game_obj.name,))
                    result = fb.set('me/cuassassins:create', game=url)
            except:
                pass
            return HttpResponseRedirect(reverse('assassins_manager.game.views.game_admin', args=(game_obj.name,)))
    else:
        form = AddGameForm()

    return render_with_metadata(request, 'form.html', '', {
        'form': form,
        'formname': 'Create Game',
        })

def is_admin(user, game):
    try:
        assassin_obj = game.assassin_set.get(user=user)
    except Assassin.DoesNotExist:
        return False

    return assassin_obj.is_admin or user.is_staff
   
@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def game_admin(request, game):
    """ Shows the game administration page """
    game_obj = get_game(game)
    if is_admin(request.user, game_obj):
        return render_with_metadata(request, 'game/admin.html', game)
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))


@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def start_game(request, game):
    """ Starts the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('are_you_sure'):
                    game_obj.start_game() # calls save internally
                    try:
                        fb = api.get_persistent_graph(request, access_token=request.user.columbiauserprofile.access_token)
                        if fb:
                            url = 'http://assassins.columbiaesc.com' + reverse('assassins_manager.game.views.details', args=(game_obj.name,))
                            result = fb.set('me/cuassassins:start', game=url)
                    except:
                        pass
                    return HttpResponseRedirect(reverse('assassins_manager.game.views.game_admin', args=(game,)))
        else:
            form = VerifyForm()
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Start Game',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def end_game(request, game):
    """ Ends the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('are_you_sure'):
                    game_obj.end_game() # calls save internally
                    return HttpResponseRedirect(reverse('assassins_manager.game.views.game_admin', args=(game,)))
        else:
            form = VerifyForm()
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'End Game',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def reset_game(request, game):
    """ Resets the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('are_you_sure'):
                    game_obj.reset_game() # calls save internally
                    return HttpResponseRedirect(reverse('assassins_manager.game.views.game_admin', args=(game,)))
        else:
            form = VerifyForm()
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Reset Game',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def delete_game(request, game):
    """ Deletes the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('are_you_sure'):
                    game_obj.delete()
                    return HttpResponseRedirect(reverse('assassins_manager.game.views.gamelist'))
        else:
            form = VerifyForm()
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Delete Game',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def add_police(request, game):
    """ Adds police to the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = AddPoliceForm(request.POST, game=game_obj)
            if form.is_valid():
                p = form.cleaned_data.get('police')
                if not p is None:
                    p.set_role(AssassinType.POLICE)
                return HttpResponseRedirect(reverse('assassins_manager.game.views.police', args=(game,)))
        else:
            form = AddPoliceForm(game=game_obj)
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Add Police',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def remove_police(request, game):
    """ Removes police from the game """
    game_obj = get_game(game)

    if is_admin(request.user, game_obj):
        if request.method == 'POST':
            form = RemovePoliceForm(request.POST, game=game_obj)
            if form.is_valid():
                p = form.cleaned_data.get('police')
                if not p is None:
                    p.set_role(AssassinType.REGULAR)
                return HttpResponseRedirect(reverse('assassins_manager.game.views.police', args=(game,)))
        else:
            form = RemovePoliceForm(game=game_obj)

        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Remove Police',
            })
    else:
        return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def join_game(request, game):
    """ Joins an asssassin to the game """
    game_obj = get_game(game)
    assassin_obj = game_obj.getAssassin(request.user)

    if request.method == 'POST':
        form = JoinGameForm(request.POST, instance=assassin_obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))
    else:
        form = JoinGameForm(instance=assassin_obj)

    return render_with_metadata(request, 'form.html', game, {
        'form': form,
        'formname': 'Join Game',
        })

@user_passes_test(lambda u: u.is_authenticated() and u.is_active)
def leave_game(request, game):
    game_obj = get_game(game)
    if game_obj.status == GameStatus.REGISTRATION:
        if request.method == 'POST':
            form = VerifyForm(request.POST)
            if form.is_valid():
                if form.cleaned_data.get('are_you_sure'):
                    assassin_obj = game_obj.getAssassin(request.user)
                    if assassin_obj:
                        if assassin_obj.squad:
                            assassin_obj.squad.remove_assassin(assassin_obj, commit=False)
                        assassin_obj.squad = None
                        assassin_obj.role = AssassinType.NOT_IN_GAME
                        assassin_obj.save()
                    return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))
        else:
            form = VerifyForm()
        return render_with_metadata(request, 'form.html', game, {
            'form': form,
            'formname': 'Leave Game',
            })
    return HttpResponseRedirect(reverse('assassins_manager.game.views.details', args=(game,)))
