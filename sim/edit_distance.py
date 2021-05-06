from sim import board_games as bg
from sim import mobile_games as mg
from sim import steam_games as sg

import nltk
import numpy as np
import pandas as pd

# board_df = pd.read_csv(r'../data/board-games/data/games_detailed_info.csv')

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
        # if query.lower()[0] == name.lower()[0]:
        if query.lower() in name.lower():
            edit_dist = nltk.edit_distance(query.lower(), name.lower())
            # query_toks = nltk.word_tokenize(query.lower())
            # name_toks = nltk.word_tokenize(name.lower())
            # ng_query = set(nltk.ngrams(query_toks, n=1, pad_right=True,))
            # ng_name = set(nltk.ngrams(name_toks, n=1, pad_right=True))
            # jaccard_dist = nltk.jaccard_distance(ng_query, ng_name)
            ranked_names.append((name, edit_dist))
    result = ''
    for tup in sorted(ranked_names, key=lambda x: x[1])[:5]:
        result += tup[0] + ';'
    return result[:-1]

# print(edit_distance_list('escape'))
