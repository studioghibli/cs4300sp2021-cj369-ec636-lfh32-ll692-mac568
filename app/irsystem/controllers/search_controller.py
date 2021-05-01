from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
import steam_games as sg
import mobile_games as mg
import board_games as bg
import edit_distance as ed


@irsystem.route('/', methods=['GET', 'POST'])
def search():
	# if request.method == 'POST':
	# 	gn = request.form['param']
	# 	ed_dis = ed.edit_distance_list(gn)
	# 	ed_dis = [x[0] for x in ed_dis]
	# 	return render_template('search.html', ed_dis=ed_dis)

	gt = request.args.get('gametype')
	gn = request.args.get('game')
	data = []

	if gn == None:
		output_message = ''
		return render_template('search.html', output_message=output_message, data=data)
	else:
		try:
			if gt == 'Board Games':
				src = 'data/board-games/data/games_detailed_info.csv'
				link = 'data/board-games/data/2019_05_02.csv'
				j = bg.boardgame_jaccard(gn, src, link)
				c = bg.boardgame_cosine_sim(gn, src)
				data = bg.combine_cosine_jaccard(c, j)
			elif gt == 'Mobile Games':
				j = mg.mgs_jaccard_list(gn)
				c = mg.mgs_jaccard_list(gn)
				l = mg.mgs_jacc_cossim(j, c)
				data = mg.mgs_get_rankings(l)
			else:
				appid = sg.steam_name_to_id[gn]
				l = sg.steam_sim_list(appid)
				data = sg.steam_get_rankings(l)
		except Exception as e:
			output_message = 'Your query was invalid. Please try searching again.'
			return render_template('search.html', output_message=output_message)
		output_message = 'Results of games similar to {' + gn + ', ' + gt + '}' + ':'
		data = data[:30]
		# data = [x[0] for x in data]
		return render_template('search.html', output_message=output_message, gt = gt,  data=data)
