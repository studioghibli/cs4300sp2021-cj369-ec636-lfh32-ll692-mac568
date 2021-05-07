import math
import numpy as np
import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

'''
GLOBAL VARIABLES
'''

# dataframe of general game info in Steam
steam_df_dict = {'appid': np.int32, 'name': str, 'platforms': str, 'categories': str,
                 'genres': str, 'steamspy_tags': str, 'positive_ratings': np.int32,
                 'negative_ratings': np.int32, 'median_playtime': np.int32, 'price': np.float32}
steam_df = pd.read_csv(r'data/steam-games/steam.csv', usecols=steam_df_dict,
                       dtype=steam_df_dict)

# dataframe of descriptions of games on Steam
steam_descriptions_df_dict = {
    'steam_appid': np.int32, 'short_description': str}
steam_descriptions_df = pd.read_csv(r'data/steam-games/steam_description_data.csv',
                                    usecols=steam_descriptions_df_dict, dtype=steam_descriptions_df_dict)

# dataframe of descriptions of games on Steam
steam_media_df_dict = {'steam_appid': np.int32, 'header_image': str}
steam_media_df = pd.read_csv(r'data/steam-games/steam_media_data.csv',
                             usecols=steam_media_df_dict, dtype=steam_media_df_dict)

# dataframe of descriptions of games on Steam
steam_links_df_dict = {'steam_appid': np.int32, 'website': str}
steam_links_df = pd.read_csv(r'data/steam-games/steam_support_info.csv',
                             usecols=steam_links_df_dict, dtype=steam_links_df_dict)

# dictionary where key is app ID and value is set of genres
steam_sets = dict()

# dictionary where key is name and value is app ID of game
steam_name_to_id = dict()

for i in range(len(steam_df['appid'])):
    steam_sets[steam_df['appid'][i]] = set(steam_df['genres'][i].split(';'))
    steam_name_to_id[steam_df['name'][i]] = steam_df['appid'][i]

'''
FUNCTIONS
'''


def steam_jaccard(appid1, appid2):
    '''
    returns Jaccard similarity score between appid1 and appid2
    '''
    return len(steam_sets[appid1].intersection(steam_sets[appid2])) \
        / len(steam_sets[appid1] | steam_sets[appid2])


def steam_jaccard_list(appid):
    '''
    returns tuple list of game app IDs and Jaccard similarity scores
    '''
    score_list = list()
    # for x in steam_df['appid']:
    for i in range(len(steam_df)):
        x = steam_df.at[i, 'appid']
        pos_ratings = steam_df.at[i, 'positive_ratings']
        neg_ratings = steam_df.at[i, 'negative_ratings']
        # rating_weight = ((pos_ratings + 1) / (neg_ratings + 2))
        rating_weight = min(((((pos_ratings + 1) / (pos_ratings + neg_ratings + 2)))
                             - (((neg_ratings + 1) / (pos_ratings + neg_ratings + 2))) + 0.5), 1)
        if x != appid:
            score_list.append((x, steam_jaccard(appid, x)))
    return score_list


tfidf_vec = TfidfVectorizer(stop_words="english")
tfidf_mat = tfidf_vec.fit_transform(steam_descriptions_df['short_description'])


def steam_cossim_list(appid):
    '''
    returns tuple list of game app IDs and cosine similarity scores
    '''
    idx = steam_descriptions_df.index[steam_descriptions_df['steam_appid'] == appid][0]
    query_tfidf = tfidf_vec.transform(
        [str(steam_descriptions_df['short_description'][idx])])
    cossims = cosine_similarity(query_tfidf, tfidf_mat).flatten()
    result = list()
    for i in range(len(cossims)):
        if i != idx:
            index = steam_df.index[steam_descriptions_df.at[i,
                                                            'steam_appid'] == steam_df['appid']]
            if len(index) > 0:
                pos_ratings = steam_df.at[index[0], 'positive_ratings']
                neg_ratings = steam_df.at[index[0], 'negative_ratings']
                rating_weight = min(((((pos_ratings + 1) / (pos_ratings + neg_ratings + 2)))
                                     - (((neg_ratings + 1) / (pos_ratings + neg_ratings + 2))) + 0.5), 1)
            else:
                rating_weight = 1
            result.append(
                (steam_descriptions_df['steam_appid'][i], cossims[i]))
    return result


def steam_sim_list(appid):
    '''
    returns tuple list of game app IDs and average of cosine and Jaccard similarity scores
    '''
    list_cosine = sorted(steam_cossim_list(appid), key=lambda x: x[0])
    list_jaccard = sorted(steam_jaccard_list(appid), key=lambda x: x[0])
    list_both = list()

    i = 0
    j = 0
    while i < len(list_cosine) and j < len(list_jaccard):
        if list_cosine[i][0] == list_jaccard[j][0]:
            list_both.append(
                (list_cosine[i][0], (list_cosine[i][1] + list_jaccard[j][1]) / 2))
            i += 1
            j += 1
        elif list_cosine[i][0] < list_jaccard[j][0]:
            i += 1
        else:
            j += 1

    return list_both


def steam_bool_filter(score_list, genres_in=None, genres_ex=None, platforms_in=None,
                      platforms_ex=None, players_in=None, players_ex=None, min_time=None,
                      max_time=None, min_price=None, max_price=None):
    '''
    returns filtered list
    * score_list: list of tuples of game app IDs and similarity scores
    * genres_in and genres_ex: list of genres to include and exclude
    * platforms_in and platforms_ex: list of platforms to include and exclude
    * players_in and players_ex: single-player or multi-player
    * min_time and max_time: minimum and maximum median playtime
    * prices_in and prices_ex: list of prices to include and exclude
    '''
    filtered = list()
    for appid, score in score_list:
        include = True
        i = steam_df.index[steam_df['appid'] == appid][0]

        genres = set(steam_df['genres'][i].split(';'))
        if genres_ex != None:
            for genre in genres_ex:
                if genre in genres:
                    include = False
                    break
            if not include:
                continue

        if genres_in != None:
            for genre in genres_in:
                if genre not in genres:
                    include = False
                    break
            if not include:
                continue

        platforms = set(steam_df['platforms'][i].split(';'))
        if platforms_ex != None:
            for platform in platforms_ex:
                if platform in platforms:
                    include = False
                    break
            if not include:
                continue

        if platforms_in != None:
            for platform in platforms_in:
                if platform not in platforms:
                    include = False
                    break
            if not include:
                continue

        categories = set(steam_df['categories'][i].split(';'))
        if players_ex != None:
            for category in players_ex:
                if category in categories:
                    include = False
                    break
            if not include:
                continue

        if players_in != None:
            for category in player_in:
                if category not in categories:
                    include = False
                    break
            if not include:
                continue

        if min_time != None:
            if steam_df['median_playtime'][i] < min_time:
                continue

        if max_time != None:
            if steam_df['median_playtime'][i] > max_time:
                continue

        if min_price != None:
            if steam_df['price'][i] < min_price:
                continue

        if max_price != None:
            if steam_df['price'][i] > max_price:
                continue

        filtered.append((appid, score))
    return filtered


def steam_get_rankings(score_list):
    '''
    list of tuples of ranked games
    * values in tuple are:
        * score: float
        * name: string
        * genres: list of strings
        * platforms: list of strings
        * price: float
        * link to image: string
        * link to site: string
    '''
    result_list = list()
    score_list = sorted(score_list, key=lambda x: x[1], reverse=True)[:30]
    for appid, score in score_list:
        i = steam_df.index[steam_df['appid'] == appid][0]
        i_web = steam_links_df.index[steam_links_df['steam_appid'] == appid]
        i_im = steam_media_df.index[steam_media_df['steam_appid'] == appid]

        if len(i_web) == 0:
            web = None
        elif type(steam_links_df['website'][i_web[0]]) == float:
            web = None
        else:
            web = steam_links_df['website'][i_web[0]]

        if len(i_im) == 0:
            im = None
        else:
            im = steam_media_df['header_image'][i_im[0]]

        result_list.append((score, steam_df['name'][i], steam_df['genres'][i].split(';'),
                            steam_df['platforms'][i].split(';'), steam_df['price'][i], im, web))
    return result_list


'''
TESTING
'''

# print('jaccard')
# output_jaccard = steam_get_rankings(steam_jaccard_list(steam_df['appid'][0]))
# print(output_jaccard)

# print('cossim')
# output_cossim = steam_get_rankings(steam_cossim_list(steam_df['appid'][0]))
# print(output_cossim)

# print('sim')
# output_sim = steam_get_rankings(steam_sim_list(steam_df['appid'][0]))
# print(output_sim)

# print('boolean and jaccard')
# output_jaccard = steam_jaccard_list(steam_df['appid'][1])
# filtered_jaccard = steam_get_rankings(steam_bool_filter(output_jaccard, genres_in=['Casual']))
# print(filtered_jaccard)

# print('boolean and cossim')
# output_cossim = steam_cossim_list(steam_df['appid'][1])
# filtered_cossim = steam_get_rankings(steam_bool_filter(output_cossim, min_price=10))
# print(filtered_cossim)

# print('boolean and sim')
# output_sim = steam_sim_list(steam_df['appid'][1])
# filtered_sim = steam_get_rankings(steam_bool_filter(output_sim, min_price=10))
# print(filtered_sim)
