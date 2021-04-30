from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd
import steam_games as sg
import mobile_games as mg
import board_games as bg


@irsystem.route('/', methods=['GET'])
def search():
	gt = request.args.get('gametype')
	gn = request.args.get('game')
	data = []
	
	if gt == None or gn == None:
		output_message = ''
		return render_template('search.html', output_message=output_message, data=data)
	else:
		try:
			if gt == 'Board Games':
				data = bg.boardgame_jaccard(gn, 'data/board-games/data/games_detailed_info.csv')
			elif gt == 'Mobile Games':
				data = mg.mgs_get_rankings(mg.mgs_jaccard_list(gn))
			else:
				data = sg.steam_get_rankings(sg.steam_jaccard_list(gn))

			output_message = 'Results of games similar to {' + \
				gn + ', ' + gt + '}' + ':'
		except Exception as e:
			output_message = 'Your query was invalid. Please try searching again.'
			return render_template('search.html', output_message=output_message)
		data = data[0:30]
		data = [x[0] for x in data]
		return render_template('search.html', output_message=output_message, data=data)
