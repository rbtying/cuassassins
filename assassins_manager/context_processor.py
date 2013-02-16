from models import * 
from forms import GameSelectForm

def header_processor(request):
    """ Context processor which adds game / assassin / squad information into the context """
    select_form = GameSelectForm()
    if not request.session.get('game_name') is None and request.user.is_authenticated():
            game_name = request.session['game_name']
            game_obj = Game.objects.get(name=game_name)
            assassin_obj = game_obj.getAssassin(request.user)
            squad = None
            if assassin_obj:
                squad = assassin_obj.squad
            additional = {'select_form': select_form, 
                    'game_current': game_obj,
                    'assassin_current': assassin_obj,
                    'squad_current': squad }
    else:
        additional = {'select_form': select_form }
    return additional
