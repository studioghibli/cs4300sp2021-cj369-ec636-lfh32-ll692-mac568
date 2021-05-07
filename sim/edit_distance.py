from sim import board_games as bg
from sim import mobile_games as mg
from sim import steam_games as sg

import nltk
import numpy as np
import pandas as pd


board_games = set(pd.Series(bg.board_details_df['primary'], dtype=str))
mobile_games = set(pd.Series(mg.mobile_games_df['App'], dtype=str))
steam_games = set(pd.Series(sg.steam_df['name'], dtype=str))

all_names = board_games | mobile_games | steam_games


def get_game_type(game):
    if game in board_games:
        return 'Board Games'
    if game in mobile_games:
        return 'Mobile Games'
    if game in steam_games:
        return 'Video Games'
    return None


def edit_distance_list(query):
    """
    returns ranked list of tuples where first value is name and second value is edit distance
    """
    ranked_names = list()
    for name in all_names:
        if query.lower() in name.lower():
            edit_dist = nltk.edit_distance(query.lower(), name.lower())
            ranked_names.append((name, edit_dist))
    result = ''
    for tup in sorted(ranked_names, key=lambda x: x[1])[:5]:
        result += tup[0] + ';'
    return result[:-1]
