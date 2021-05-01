from sim import board_games as bg
from sim import mobile_games as mg
from sim import steam_games as sg

import numpy as np
import pandas as pd

board_df = pd.read_csv(r'data/board-games/data/games_detailed_info.csv')

board_games = set(pd.Series(board_df['primary'], dtype=str))
mobile_games = set(pd.Series(mg.game_apps['App'], dtype=str))
steam_games = set(pd.Series(sg.steam_df['name'], dtype=str))

all_names = board_games | mobile_games | steam_games

def insertion_cost(message, j):
    return 1

def deletion_cost(query, i):
    return 1

def substitution_cost(query, message, i, j):
    if query[i-1] == message[j-1]:
        return 0
    else:
        return 2

def edit_matrix(query, message):
    """ calculates the edit matrix
    
    Arguments
    =========
    query: query string,
    message: message string,
    m: length of query + 1,
    n: length of message + 1,
    
    Returns:
        edit matrix {(i,j): int}
    """
    
    m = len(query) + 1
    n = len(message) + 1
    
    matrix = np.zeros((m, n))
    for i in range(1, m):
        matrix[i, 0] = matrix[i-1, 0] + deletion_cost(query, i)
    
    for j in range(1, n):
        matrix[0, j] = matrix[0, j-1] + insertion_cost(message, j)
    
    for i in range(1, m):
        for j in range(1, n):
            matrix[i, j] = min(
                matrix[i-1, j] + deletion_cost(query, i),
                matrix[i, j-1] + insertion_cost(message, j),
                matrix[i-1, j-1] + substitution_cost(query, message, i, j)
            )
    
    return matrix

def edit_distance(query, message):
    """ Edit distance calculator
    
    Arguments
    =========
    query: query string,    
    message: message string,
    
    Returns:
        edit cost (int)
    """
    query = query.lower()
    message = message.lower()
    
    edit_mat = edit_matrix(query, message)
    return edit_mat[len(query), len(message)]

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
        ranked_names.append((name, edit_distance(query, name)))
    result = ''
    for tup in sorted(ranked_names, key=lambda x: x[1])[:5]:
        result += tup[0] + ';'
    return result
# print(edit_distance_list('hello'))
# print(edit_distance_list('stanley'))