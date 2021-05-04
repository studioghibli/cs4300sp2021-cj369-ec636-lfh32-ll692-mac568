from sim import board_games as bg
from sim import mobile_games as mg
from sim import steam_games as sg

import nltk
import numpy as np
import pandas as pd

board_df = pd.read_csv(r'data/board-games/data/games_detailed_info.csv')

board_games = set(pd.Series(board_df['primary'], dtype=str))
mobile_games = set(pd.Series(mg.mobile_games_df['App'], dtype=str))
steam_games = set(pd.Series(sg.steam_df['name'], dtype=str))

all_names = board_games | mobile_games | steam_games


def edit_distance_list(query, game_type):
    """
    returns ranked list of tuples where first value is name and second value is edit distance
    """
    ranked_names = list()
    all_names = list()
    if game_type == 'Board Games':
        all_names = board_games
    elif game_type == 'Mobile Games':
        all_names = mobile_games
    elif game_type == 'Video Games':
        all_names = steam_games
    for name in all_names:
        if query[0].lower() == name[0].lower():
            ranked_names.append(
                (name, nltk.edit_distance(query.lower(), name.lower())))
    result = ''
    for tup in sorted(ranked_names, key=lambda x: x[1])[:5]:
        result += tup[0] + ';'
    return result[:-1]