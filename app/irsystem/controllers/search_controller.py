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
	k = request.args.get('keys')

	if gt == None or gn == None:
		data = []
		output_message = ''
		return render_template('search.html', output_message=output_message, data=data)
	else:
		try:
			if gt == 'boardgames':
				data = bg.boardgame_jaccard(gn, 'data/board-games/data/games_detailed_info.csv')
			elif gt == 'mobilegames':
				data = mg.mgs_get_rankings(mg.mgs_jaccard_list(gn))
			else:
				data = sg.steam_get_rankings(sg.steam_jaccard_list(gn))

			output_message = 'Results of games similar to {' + \
				gn + ', ' + k + ', ' + gt + '}' + ':'
		except Exception as e:
			output_message = 'Your query was invalid. Please try searching again.'
			return render_template('search.html', output_message=output_message)
		
		return render_template('search.html', output_message=output_message, data=data)
