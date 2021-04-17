import pandas as pd
import numpy as np


def boardgame_jaccard(game_title, boardgame_data):
    boardgames_df = pd.read_csv(boardgame_data)
    
    shape = boardgames_df.shape
    num_boardgames = shape[0]
    sims_jac = []
    try:
        index = boardgames_df.index
        game_index = index[boardgames_df['primary'] == game_title]
        game_genres = boardgames_df.at[game_index[0], 'boardgamecategory'][1:-1].replace("'", "")
        game_genres = set(game_genres.split(','))
    except TypeError:
        game_genres = []
    
    for i in range(num_boardgames):
        try:
            cat_i = boardgames_df.at[i,'boardgamecategory'][1:-1].replace("'", "")
            cat_i = set(cat_i.split(','))
        except TypeError:
            cat_i = []
        if len(cat_i) == 0 or len(game_genres) == 0:
            sims_jac.append(([boardgames_df.at[i,'primary']],0))
        else:
            sims_jac.append(([boardgames_df.at[i,'primary']],(len(cat_i & game_genres) / len(cat_i | game_genres))))
        
    return sorted(sims_jac, key=lambda x: -x[1])

print(boardgame_jaccard('XCOM: The Board Game', 'games_detailed_info.csv'))