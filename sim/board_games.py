import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

board_df_dict = {'id': np.int64, 'url': str}
board_df = pd.read_csv(
    r'data/board-games/data/2019_05_02.csv', usecols=board_df_dict, dtype=board_df_dict)

board_details_df_dict = {'primary': str, 'description': str, 'boardgamecategory': str, 'boardgamemechanic': str,
                         'image': str, 'minplaytime': np.int64, 'maxplaytime': np.int64, 'minplayers': np.int16, 'maxplayers': np.int16,
                         'bayesaverage': np.float32, 'id': np.int32}
board_details_df = pd.read_csv(
    r'data/board-games/data/games_detailed_info.csv', usecols=board_details_df_dict, dtype=board_details_df_dict)


def boardgame_jaccard(game_title):
    shape = board_details_df.shape
    num_boardgames = shape[0]
    sims_jac = []

    try:
        index = board_details_df.index
        game_index = index[game_title == board_details_df['primary']]
        game_genres = board_details_df.at[game_index[0],
                                          'boardgamecategory'][1:-1].replace("'", "")
        game_genres = set(game_genres.split(','))
    except TypeError:
        game_genres = []

    for i in range(num_boardgames):
        if board_details_df.at[i, 'primary'] != game_title:
            try:
                cat_i = board_details_df.at[i,
                                            'boardgamecategory'][1:-1].replace("'", "")
                cat_i = cat_i.replace("\"", "")
                cat_i = set(cat_i.split(','))
            except TypeError:
                cat_i = []

            try:
                mech_i = board_details_df.at[i,
                                             'boardgamemechanic'][1:-1].replace("'", "")
                mech_i = mech_i.replace("\"", "")
                mech_i = set(mech_i.split(','))
            except TypeError:
                mech_i = []

            image = board_details_df.at[i, 'image']

            index_l = board_df.index
            link_index = index_l[board_details_df.at[i,
                                                     'id'] == board_df['id']]
            link = "https://boardgamegeek.com" + \
                board_df.at[link_index[0], 'url']

            rating = board_details_df.at[i, 'bayesaverage']
            rating_weight = (rating / 10) + 1

            min_time = board_details_df.at[i, 'minplaytime']
            max_time = board_details_df.at[i, 'maxplaytime']
            min_players = board_details_df.at[i, 'minplayers']
            max_players = board_details_df.at[i, 'maxplayers']
            if len(cat_i) == 0 or len(game_genres) == 0:
                sims_jac.append((board_details_df.at[i, 'primary'], 0, image, link,
                                cat_i, mech_i, min_time, max_time, min_players, max_players))
            else:
                sims_jac.append((board_details_df.at[i, 'primary'], (len(cat_i & game_genres) / len(cat_i | game_genres)) * rating_weight, image,
                                 link, cat_i, mech_i, min_time, max_time, min_players, max_players))

    return sorted(sims_jac, key=lambda x: x[0])


tfidf_vec = TfidfVectorizer(stop_words="english")
tfidf_mat = tfidf_vec.fit_transform(board_details_df['description'].fillna(''))


def boardgame_cosine_sim(game_title):
    idx = board_details_df.index[board_details_df['primary'] == game_title][0]
    query_tfidf = tfidf_vec.transform(
        [str(board_details_df['description'][idx])])
    cossims = cosine_similarity(query_tfidf, tfidf_mat).flatten()
    result = list()
    for i in range(len(cossims)):
        if i != idx:
            rating = board_details_df.at[i, 'bayesaverage']
            rating_weight = (rating / 10) + 1
            result.append(
                (board_details_df['primary'][i], cossims[i] * rating_weight))
    return sorted(result, key=lambda x: x[0])


def combine_cosine_jaccard(cosine_list, jaccard_list):
    combine_list = []
    for game in range(len(cosine_list)):
        combine_list.append((jaccard_list[game][0], (cosine_list[game][1] + jaccard_list[game][1]) / 2,
                             jaccard_list[game][2], jaccard_list[game][3], jaccard_list[game][4],
                             jaccard_list[game][5], jaccard_list[game][6], jaccard_list[game][7],
                             jaccard_list[game][8], jaccard_list[game][9]))

    return sorted(combine_list, key=lambda x: -x[1])


def boardgames_boolean(similar_games, disliked_games=None, liked_genres=None, disliked_genres=None, liked_mechanics=None,
                       disliked_mechanics=None, min_time=None, max_time=None, min_players=None, max_players=None):
    filtered_games = []
    for game in similar_games:
        include = True

        if liked_genres != None:
            for genre in liked_genres:
                if genre not in game[4]:
                    include = False
                    break
            if not include:
                continue

        if disliked_genres != None:
            for genre in disliked_genres:
                if genre in game[4]:
                    include = False
                    break
            if not include:
                continue

        if liked_mechanics != None:
            for mechanic in liked_mechanics:
                if mechanic not in game[5]:
                    include = False
                    break
            if not include:
                continue

        if disliked_mechanics != None:
            for mechanic in disliked_mechanics:
                if mechanic in game[5]:
                    include = False
                    break
            if not include:
                continue

        if min_time != None:
            if game[6] < min_time:
                continue

        if max_time != None:
            if game[7] > max_time:
                continue

        if min_players != None:
            if game[8] < min_time:
                continue

        if max_players != None:
            if game[9] > max_time:
                continue

        filtered_games.append(game)

    return filtered_games


def get_categories():
    categories = set()

    game_genres = pd.Series(board_details_df['boardgamecategory'])
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


def get_mechanics():
    mechanics = set()

    game_mechanics = pd.Series(board_details_df['boardgamemechanic'])
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

# jaccard = boardgame_jaccard('XCOM: The Board Game')
# cosine = boardgame_cosine_sim('XCOM: The Board Game')
# print(jaccard)
# print(cosine)
# game_list = combine_cosine_jaccard(cosine, jaccard)
# print(game_list[:10])
# filtered = boardgames_boolean(game_list, disliked_games=['Project: ELITE'], disliked_genres=['Trivia'], liked_genres=['Puzzle'],
#                               liked_mechanics=['Tile Placement'])
# print(filtered)
# print(get_categories())
# print(get_mechanics())
