import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def boardgame_jaccard(game_title, boardgame_data, link_data):
    boardgames_df = pd.read_csv(boardgame_data)
    links_df = pd.read_csv(link_data)
    
    shape = boardgames_df.shape
    num_boardgames = shape[0]
    sims_jac = []
    
    # game_titles = pd.Series(boardgames_df['primary']).str.lower()
    # game_indices = pd.Series(game_titles.str.contains(game_title, case=False, regex=False))
    # matching_games = game_indices[game_indices].index

    try:
        index = boardgames_df.index
        game_index = index[game_title == boardgames_df['primary']]
        # game_index = matching_games[0]
        game_genres = boardgames_df.at[game_index[0], 'boardgamecategory'][1:-1].replace("'", "")
        game_genres = set(game_genres.split(','))
    except TypeError:
        game_genres = []
    
    for i in range(num_boardgames):
        if boardgames_df.at[i,'primary'] != game_title:
            try:
                cat_i = boardgames_df.at[i,'boardgamecategory'][1:-1].replace("'", "")
                cat_i = cat_i.replace("\"", "")
                cat_i = set(cat_i.split(','))
            except TypeError:
                cat_i = []
                
            try:
                mech_i  = boardgames_df.at[i,'boardgamemechanic'][1:-1].replace("'", "")
                mech_i = mech_i.replace("\"", "")
                mech_i = set(mech_i.split(','))
            except TypeError:
                mech_i = []
            
            image = boardgames_df.at[i,'image']
                
            index_l = links_df.index
            link_index = index_l[boardgames_df.at[i,'id'] == links_df['id']]
            link = "https://boardgamegeek.com" + links_df.at[link_index[0], 'url']
            
            min_time = boardgames_df.at[i,'minplaytime']
            max_time = boardgames_df.at[i,'maxplaytime']
            min_players = boardgames_df.at[i,'minplayers']
            max_players = boardgames_df.at[i,'maxplayers']
            if len(cat_i) == 0 or len(game_genres) == 0:
                sims_jac.append((boardgames_df.at[i,'primary'],0, image, link, cat_i, mech_i, min_time, max_time, min_players, max_players))
            else:
                sims_jac.append((boardgames_df.at[i,'primary'],(len(cat_i & game_genres) / len(cat_i | game_genres)), image, link, cat_i, mech_i,
                                 min_time, max_time, min_players, max_players))
        
    return sorted(sims_jac, key=lambda x: x[0])
    # return sorted(sims_jac, key=lambda x: -x[1])

def boardgame_cosine_sim(game_title, boardgame_data):
    boardgames_df = pd.read_csv(boardgame_data)
    shape = boardgames_df.shape
    num_boardgames = shape[0]
    cosine_sims = []
    
    index = boardgames_df.index
    game_index = index[boardgames_df['primary'] == game_title]
    
    # game_titles = pd.Series(boardgames_df['primary']).str.lower()
    # game_indices = pd.Series(game_titles.str.contains(game_title, case=False, regex=False))
    # matching_games = game_indices[game_indices].index
    # game_index = matching_games[0]
    
    game_desc = boardgames_df.at[game_index[0], 'description']
    
    tfidf_vec = TfidfVectorizer(stop_words="english")
    descriptions = []
    for i in range(num_boardgames):
        script_i = boardgames_df.at[i, 'description']
        if pd.isnull(script_i):
            descriptions.append('')
        else:
            descriptions.append(script_i)
        
    tfidf_mat = tfidf_vec.fit_transform(descriptions).toarray()
    
    for i in range(num_boardgames):
        q = tfidf_mat[i]
        d = tfidf_mat[game_index[0]]
        if boardgames_df.at[i,'primary'] != game_title:
            if np.linalg.norm(q) * np.linalg.norm(d) == 0:
                cosine_sims.append((boardgames_df.at[i,'primary'], 0))
            else:
                cosine_sims.append((boardgames_df.at[i,'primary'], (np.dot(q, d)) / (np.linalg.norm(q) * np.linalg.norm(d))))
    
    return sorted(cosine_sims)
    # return sorted(cosine_sims, key=lambda x: -x[1])
        
        
def combine_cosine_jaccard(cosine_list, jaccard_list):
    combine_list = []
    for game in range(len(cosine_list)):
        combine_list.append((cosine_list[game][0], (cosine_list[game][1] + jaccard_list[game][1]) / 2, jaccard_list[game][2], jaccard_list[game][3],
                             jaccard_list[game][4], jaccard_list[game][5], jaccard_list[game][6], jaccard_list[game][7], jaccard_list[game][8],
                             jaccard_list[game][9]))
    
    return sorted(combine_list, key=lambda x: -x[1])


def boardgames_boolean(similar_games, disliked_games=['None'], disliked_genres=['None'], liked_genres=[], liked_mechanics=[],
                       disliked_mechanics=['None'], min_time=0, max_time=float('inf'), min_players=0, max_players=float('inf')):
    filtered_games = []
    for game in similar_games:
        if game[0] not in disliked_games:
            for genre in disliked_genres:
                try:
                    if genre not in game[4]:
                        for mechanic in disliked_mechanics:
                            if mechanic not in game[5]:
                                for genre in liked_genres:
                                    if genre not in game[4]:
                                        raise TypeError
                                for mechanic in liked_mechanics:
                                    if mechanic not in game[5]:
                                        raise TypeError
                                if (game[6] > min_time and game[7] < max_time and game[8] > min_players and game[9] < max_players):
                                    filtered_games.append(game)
                except TypeError:
                    pass
                    
    return filtered_games

def get_categories(boardgame_data):
    boardgames_df = pd.read_csv(boardgame_data)
    categories = set()
    
    game_genres = pd.Series(boardgames_df['boardgamecategory'])
    for genres in game_genres:
        try:
            cat_i = genres[1:-1].replace("'", "")
            cat_i = cat_i.replace("\"", "")
            cat_i = set(cat_i.split(','))
        except TypeError:
            cat_i = []
        for genre in cat_i:
            categories.add(genre.strip())
        
    return sorted(list(categories))
    
def get_mechanics(boardgame_data):
    boardgames_df = pd.read_csv(boardgame_data)
    mechanics = set()
    
    game_mechanics = pd.Series(boardgames_df['boardgamemechanic'])
    for mechs in game_mechanics:
        try:
            mech_i = mechs[1:-1].replace("'", "")
            mech_i = mech_i.replace("\"", "")
            mech_i = set(mech_i.split(','))
        except TypeError:
            mech_i = []
        for mechanic in mech_i:
            mechanics.add(mechanic.strip())
        
    return sorted(list(mechanics))

        
# jaccard = boardgame_jaccard('XCOM: The Board Game', 'data/board-games/data/games_detailed_info.csv', 'data/board-games/data/2019_05_02.csv')
# cosine = boardgame_cosine_sim('XCOM: The Board Game', 'data/board-games/data/games_detailed_info.csv')
# print(boardgame_jaccard('XCOM: The Board Game', 'data/board-games/data/games_detailed_info.csv', 'data/board-games/data/2019_05_02.csv'))
# print(boardgame_cosine_sim('xcom', 'data/board-games/data/games_detailed_info.csv'))
# game_list = boardgame_cosine_sim('XCOM: The Board Game', 'data/board-games/data/games_detailed_info.csv')
# game_list = combine_cosine_jaccard(cosine, jaccard)
# print(boardgames_boolean(game_list, disliked_games=['Project: ELITE'], disliked_genres=['Trivia'],liked_genres=['Puzzle'],
#                          liked_mechanics=['Tile Placement']))
# print(combine_cosine_jaccard(cosine, jaccard))
# print(get_categories('data/board-games/data/games_detailed_info.csv'))
# print(get_mechanics('data/board-games/data/games_detailed_info.csv'))