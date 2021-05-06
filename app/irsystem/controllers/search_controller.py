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
    gn = request.args.get('game')
    gt = ed.get_game_type(gn)
    data = []

    if request.method == 'POST':
        json = request.get_json()
        if json != None:
            gi = []
            ge = []
            len1 = 0
            len2 = 0
            for j in json['gi'].keys():
                try:
                    if isinstance(int(j), int):
                        gi.extend([json['gi'][j]])
                except Exception as l:
                    continue
            for k in json['ge'].keys():
                try:
                    if isinstance(int(k), int):
                        ge.extend([json['ge'][k]])
                except Exception as o:
                    continue
            try:
                if gt == 'Board Games':
                    src = 'data/board-games/data/games_detailed_info.csv'
                    link = 'data/board-games/data/2019_05_02.csv'
                    j = bg.boardgame_jaccard(gn, src, link)
                    c = bg.boardgame_cosine_sim(gn, src)
                    d = bg.combine_cosine_jaccard(c, j)
                    data = bg.boardgames_boolean(d, ['None'], ge, gi, [],  [
                                                 'None'], 0, float('inf'), 0, float('inf'))
                elif gt == 'Mobile Games':
                    j = mg.mgs_jaccard_list(gn)
                    c = mg.mgs_cossim_list(gn)
                    l = mg.mgs_jacc_cossim(j, c)
                    d = mg.mgs_get_rankings(l)
                    data = mg.mgs_boolean_filter(d, gi, ge)
                else:
                    appid = sg.steam_name_to_id[gn]
                    d = sg.steam_bool_filter(sg.steam_sim_list(
                        appid), genres_in=gi, genres_ex=ge)
                    data = sg.steam_get_rankings(d)[:30]
            except Exception as n:
                output_message = 'Your query was invalid. Please try searching again.'
                return render_template('search.html', output_message=output_message)
            output_message = gn
            return jsonify({'gt': gt, 'data': str(data)})
        else:
            return ed.edit_distance_list(request.form['game_name'])

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
        output_message = gn
        return render_template('search.html', output_message=output_message, gt=gt, data=data)
