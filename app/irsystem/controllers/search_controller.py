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
				name_id = {}
				id_name = {}
				for i in range(len(steam_df['name'])):
					name_id[steam_df['name'][i]] = steam_df['appid'][i]
					id_name[str(steam_df['appid'][i])] = steam_df['name'][i]

				pdata = sg.steam_get_rankings(sg.steam_jaccard_list(name_id[gn]))
				data = []
				for l in range(0, len(pdata)):
					data.append([(id_name[str(pdata[l][0])], pdata[l][1])])

			output_message = 'Results of games similar to {' + \
				gn + ', ' + k + ', ' + gt + '}' + ':'
		except Exception as e:
			output_message = 'Your query was invalid. Please try searching again.'
			return render_template('search.html', output_message=output_message)
		
		return render_template('search.html', output_message=output_message, data=data)
