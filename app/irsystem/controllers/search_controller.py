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
        try:
            return ed.edit_distance_list(request.form['game_name'])
        except:
            gn = request.form['gn']
            gt = ed.get_game_type(gn)

            fil1in = request.form['filter_1_in']
            fil1out = request.form['filter_1_out']

            fil2in = request.form['filter_2_in']
            fil2out = request.form['filter_2_out']

            fil3in = request.form['filter_3_in']
            fil3out = request.form['filter_3_out']

            fil4in = request.form['filter_4_in']
            fil4out = request.form['filter_4_out']

            fil5in = request.form['filter_5_in']
            fil5out = request.form['filter_5_out']

            try:
                if gt == 'Board Games':
                    j = bg.boardgame_jaccard(gn)
                    c = bg.boardgame_cosine_sim(gn)
                    j_c = bg.combine_cosine_jaccard(c, j)
                    data = bg.boardgames_boolean(j_c, liked_genres=fil1in, disliked_genres=fil1out, liked_mechanics=fil2in,
                                                 disliked_mechanics=fil2out, min_time=fil3in, max_time=fil3out, min_players=fil4in, max_players=fil4out)
                elif gt == 'Mobile Games':
                    j = mg.mgs_jaccard_list(gn)
                    c = mg.mgs_cossim_list(gn)
                    l = mg.mgs_jacc_cossim(j, c)
                    filtered_l = mg.mgs_boolean_filter(
                        l, included_genres=fil1in, excluded_genres=fil1out, min_price=fil2in, max_price=fil2out, min_rating=fil3in)
                    data = mg.mgs_get_rankings(l)[:30]
                else:
                    appid = sg.steam_name_to_id[gn]
                    l = sg.steam_get_rankings(sg.steam_sim_list(appid))
                    data = sg.steam_bool_filter(l, genres_in=fil1in, genres_ex=fil1out, platforms_in=fil2in, platforms_ex=fil2out,
                                                players_in=fil3in, players_ex=fil3out, min_time=fil4in, max_time=fil4out, min_price=fil5in, max_price=fil5out)
            except Exception as e:
                output_message = 'invalid query'
                return render_template('search.html', output_message=output_message)

            output_message = gn
            return render_template('search.html', output_message=output_message, gt=gt, data=data)

    else:
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
                output_message = 'invalid query'
                return render_template('search.html', output_message=output_message)
            output_message = gn
            return render_template('search.html', output_message=output_message, gt=gt, data=data)
