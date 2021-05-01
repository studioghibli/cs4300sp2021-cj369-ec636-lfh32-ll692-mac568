import math
import numpy as np
import pandas as pd
import re

from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

'''
GLOBAL VARIABLES
'''

# dataframe of general game info in Steam
steam_df_dict = {'appid': np.int32, 'name': str, 'platforms': str, 'genres': str, \
    'steamspy_tags': str, 'median_playtime': np.int32, 'price': np.float32 }
steam_df = pd.read_csv(r'data/steam-games/steam.csv', usecols=steam_df_dict, \
    dtype=steam_df_dict)

# dataframe of descriptions of games on Steam
steam_descriptions_df_dict = {'steam_appid': np.int32, 'short_description': str }
steam_descriptions_df = pd.read_csv(r'data/steam-games/steam_description_data.csv', \
    usecols=steam_descriptions_df_dict, dtype=steam_descriptions_df_dict)

# dataframe of descriptions of games on Steam
steam_media_df_dict = {'steam_appid': np.int32, 'header_image': str }
steam_media_df = pd.read_csv(r'data/steam-games/steam_media_data.csv', \
    usecols=steam_media_df_dict, dtype=steam_media_df_dict)

# dataframe of descriptions of games on Steam
steam_links_df_dict = {'steam_appid': np.int32, 'website': str }
steam_links_df = pd.read_csv(r'data/steam-games/steam_support_info.csv', \
    usecols=steam_links_df_dict, dtype=steam_links_df_dict)

# dictionary where key is app ID and value is set of genres
steam_sets = dict()

# dictionary where key is name and value is app ID of game
steam_name_to_id = dict()

# dictionary where key is app ID and value is index in steam_df
steam_id_to_idx = dict()

for i in range(len(steam_df['appid'])):
    steam_sets[steam_df['appid'][i]] = set(steam_df['genres'][i].split(';'))
    steam_name_to_id[steam_df['name'][i]] = steam_df['appid'][i]
    steam_id_to_idx[steam_df['appid'][i]] = i

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
    for x in steam_df['appid']:
        if x != appid:
            score_list.append((x, steam_jaccard(appid, x)))
    return score_list

def steam_cossim_list(appid):
    '''
    returns tuple list of game app IDs and cosine similarity scores
    '''
    # tfidf_mat contains tf-idf vectors
    tfidf_vec = TfidfVectorizer(stop_words="english")
    tfidf_mat = tfidf_vec.fit_transform(list(steam_descriptions_df['short_description'])).toarray()

    idx = steam_id_to_idx[appid]
    result = list()
    for i in range(steam_descriptions_df.shape[0]):
        q = tfidf_mat[i]
        d = tfidf_mat[idx]
        if i != idx:
            if np.linalg.norm(q) * np.linalg.norm(d) == 0:
                result.append((steam_descriptions_df['steam_appid'][i], 0))
            else:
                result.append((steam_descriptions_df['steam_appid'][i], \
                    (np.dot(q, d)) / (np.linalg.norm(q) * np.linalg.norm(d))))
    
    return result

def steam_sim_list(appid):
    '''
    returns tuple list of game app IDs and average of cosine and Jaccard similarity scores
    '''
    list_cosine = steam_cossim_list(appid)
    list_jaccard = steam_jaccard_list(appid)
    list_both = list()

    i = 0
    j = 0
    while i < len(list_cosine) and j < len(list_jaccard):
        if list_cosine[i][0] == list_jaccard[j][0]:
            list_both.append((list_cosine[i][0], (list_cosine[i][1] + list_jaccard[j][1]) / 2))
            i += 1
            j += 1
        elif list_cosine[i][0] < list_jaccard[j][0]:
            i += 1
        else:
            j += 1
        
    return list_both

def steam_bool_filter(score_list, genres_in=None, genres_ex=None, platforms_in=None, \
    platforms_ex=None, players_in=None, players_ex=None, min_time=None, \
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
        i = steam_id_to_idx[appid]

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
        i = steam_id_to_idx[appid]
        if type(steam_links_df['website'][i]) == float:
            web = None
        else:
            web = steam_links_df['website'][i]
        result_list.append((score, steam_df['name'][i], steam_df['genres'][i].split(';'), \
            steam_df['platforms'][i].split(';'), steam_df['price'][i], \
            steam_media_df['header_image'][i], web))
    return result_list

'''
TESTING
'''

# print('jaccard')
# output_jaccard = steam_get_rankings(steam_jaccard_list(steam_df['appid'][0]))
# print(output_jaccard)

# print('cossim')
# output_cossim = steam_get_rankings(steam_cossim_list(1069460))
# print(output_cossim)

# print('sim')
# output_sim = steam_get_rankings(steam_sim_list(1069460))
# print(output_sim)

# print('boolean and jaccard')
# output_jaccard = steam_jaccard_list(steam_df['appid'][0])
# filtered_jaccard = steam_get_rankings(steam_bool_filter(output_jaccard, genres_in=['Casual']))
# print(filtered_jaccard)

# print('boolean and cossim')
# output_cossim = steam_cossim_list(steam_df['appid'][0])
# filtered_cossim = steam_get_rankings(steam_bool_filter(output_cossim, min_price=10))
# print(filtered_cossim)

# print('boolean and sim')
# output_sim = steam_sim_list(steam_df['appid'][0])
# filtered_sim = steam_get_rankings(steam_bool_filter(output_sim, min_price=10))
# print(filtered_sim)