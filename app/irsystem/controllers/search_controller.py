from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
from sim import steam_games as sg
from sim import mobile_games as mg
from sim import board_games as bg
from sim import edit_distance as ed


@irsystem.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        return ed.edit_distance_list(request.form['game_name'])

    # gt = request.args.get('gametype')
    gn = request.args.get('game')
    gt = ed.get_game_type(gn)
    data = []

    if gt == None or gn == None:
        output_message = ''
        return render_template('search.html', output_message=output_message, data=data)
    else:
        try:
            if gt == 'Board Games':
                j = bg.boardgame_jaccard(gn)
                c = bg.boardgame_cosine_sim(gn)
                data = bg.combine_cosine_jaccard(c, j)[:30]
            elif gt == 'Mobile Games':
                j = mg.mgs_jaccard_list(gn)
                c = mg.mgs_cossim_list(gn)
                l = mg.mgs_jacc_cossim(j, c)
                data = mg.mgs_get_rankings(l)[:30]
            else:
                appid = sg.steam_name_to_id[gn]
                data = sg.steam_get_rankings(sg.steam_sim_list(appid))[:30]
        except Exception as e:
            output_message = 'Your query was invalid. Please try searching again.'
            return render_template('search.html', output_message=output_message)
        output_message = 'Results of games similar to: ' + gn
        return render_template('search.html', output_message=output_message, gt=gt, data=data)