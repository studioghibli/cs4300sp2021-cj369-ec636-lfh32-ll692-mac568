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
            gt = request.form['gt']

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
                    if fil1in == '':
                        fil1in = None
                    else:
                        fil1in = fil1in.split(';')[:-1]
                    if fil1out == '':
                        fil1out = None
                    else:
                        fil1out = fil1out.split(';')[:-1]
                    if fil2in == '':
                        fil2in = None
                    else:
                        fil2in = fil2in.split(';')[:-1]
                    if fil2out == '':
                        fil2out = None
                    else:
                        fil2out = fil2out.split(';')[:-1]
                    if fil3in == '':
                        fil3in = None
                    else:
                        fil3in = int(fil3in)
                    if fil3out == '':
                        fil3out = None
                    else:
                        fil3out = int(fil3out)
                    if fil4in == '':
                        fil4in = None
                    else:
                        fil4in = int(fil4in)
                    if fil4out == '':
                        fil4out = None
                    else:
                        fil4out = int(fil4out)
                    if fil5in == '':
                        fil5in = None

                    j = bg.boardgame_jaccard(gn)
                    c = bg.boardgame_cosine_sim(gn)
                    data = bg.boardgames_boolean(bg.combine_cosine_jaccard(c, j), liked_genres=fil1in, disliked_genres=fil1out, liked_mechanics=fil2in,
                                                 disliked_mechanics=fil2out, min_time=fil3in, max_time=fil3out, min_players=fil4in, max_players=fil4out)[:30]
                elif gt == 'Mobile Games':
                    if fil1in == '':
                        fil1in = None
                    else:
                        fil1in = fil1in.split(';')[:-1]
                    if fil1out == '':
                        fil1out = None
                    else:
                        fil1out = fil1out.split(';')[:-1]
                    if fil2in == '':
                        fil2in = None
                    else:
                        fil2in = float(fil2in)
                    if fil2out == '':
                        fil2out = None
                    else:
                        fil2out = float(fil2out)
                    if fil3in == '':
                        fil3in = None
                    else:
                        fil3in = float(fil3in)

                    l = mg.mgs_jacc_cossim(
                        mg.mgs_jaccard_list(gn), mg.mgs_cossim_list(gn))
                    filtered_l = mg.mgs_boolean_filter(
                        l, included_genres=fil1in, excluded_genres=fil1out, min_price=fil2in, max_price=fil2out, min_rating=fil3in)
                    data = mg.mgs_get_rankings(l)[:30]
                elif gt == "Video Games":
                    if fil1in == '':
                        fil1in = None
                    else:
                        fil1in = fil1in.split(';')[:-1]
                    if fil1out == '':
                        fil1out = None
                    else:
                        fil1out = fil1out.split(';')[:-1]
                    if fil2in == '':
                        fil2in = None
                    else:
                        fil2in = fil2in.split(';')[:-1]
                    if fil2out == '':
                        fil2out = None
                    else:
                        fil2out = fil2out.split(';')[:-1]
                    if fil3in == '':
                        fil3in = None
                    else:
                        fil3in = fil3in.split(';')[:-1]
                    if fil3out == '':
                        fil3out = None
                    else:
                        fil3out = fil3out.split(';')[:-1]
                    if fil4in == '':
                        fil4in = None
                    else:
                        fil4in = int(fil4in)
                    if fil4out == '':
                        fil4out = None
                    else:
                        fil4out = int(fil4out)
                    if fil5in == '':
                        fil5in = None
                    else:
                        fil5in = float(fil5in)
                    if fil5out == '':
                        fil5out = None
                    else:
                        fil5out = float(fil5out)

                    appid = sg.steam_name_to_id[gn]
                    data = sg.steam_get_rankings(sg.steam_bool_filter(sg.steam_sim_list(appid), genres_in=fil1in, genres_ex=fil1out, platforms_in=fil2in, platforms_ex=fil2out,
                                                                      players_in=fil3in, players_ex=fil3out, min_time=fil4in, max_time=fil4out, min_price=fil5in, max_price=fil5out))

                output_message = gn
                return render_template('search.html', output_message=output_message, gt=gt, data=data)
            except Exception as e:
                output_message = 'invalid query'
                return render_template('search.html', output_message=output_message)

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
                    l = sg.steam_sim_list(appid)
                    data = sg.steam_get_rankings(l)[:30]
            except Exception as e:
                output_message = 'invalid query'
                return render_template('search.html', output_message=output_message)
            output_message = gn
            return render_template('search.html', output_message=output_message, gt=gt, data=data)
