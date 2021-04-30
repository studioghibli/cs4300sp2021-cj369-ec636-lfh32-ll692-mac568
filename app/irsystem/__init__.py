from flask import Blueprint

# Define a Blueprint for this module (mchat)
irsystem = Blueprint('irsystem', __name__, url_prefix='/',static_folder='static',template_folder='templates')

# Import all controllers
from .controllers.search_controller import *

from .controllers.popular_controller import *

from .controllers.mobilegames_controller import *

from .controllers.videogames_controller import *

from .controllers.boardgames_controller import *

from .controllers.account_controller import *
