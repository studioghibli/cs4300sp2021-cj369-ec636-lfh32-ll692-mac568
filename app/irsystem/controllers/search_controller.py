from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import pandas as pd



@irsystem.route('/', methods=['GET'])
def search():
	gt = request.args.get('gametype')
	gn = request.args.get('game')
	k = request.args.get('keys')

	if gt == None or gn == None or k == None:
		data = []
		output_message = ''
	else:
		if gt == 'boardgames':
			data = list(pd.read_csv(r'app/datasets/steam.csv'))
		elif gt == 'mobilegames':
			data = list(pd.read_csv(r'app/datasets/bg_detailed_info.csv'))
		else:
			data = list(pd.read_csv(r'app/datasets/googleplaystore.csv'))
		
		output_message = "Your search: " + gt + ', ' + gn + ', ' + k
	return render_template('search.html', output_message=output_message, data=data)