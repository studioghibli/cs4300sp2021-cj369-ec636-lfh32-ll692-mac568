import math
import numpy as np
import pandas as pd
import re

from collections import Counter

'''
GLOBAL VARIABLES
'''

# dataframe of general game info in Steam
steam_df = pd.read_csv(r'data/steam-games/steam.csv')

# dataframe of descriptions of games on Steam
steam_descriptions_df = pd.read_csv(r'data/steam-games/steam_description_data.csv')

# dataframe of descriptions of games on Steam
steam_media_df = pd.read_csv(r'data/steam-games/steam_media_data.csv')

# dataframe of descriptions of games on Steam
steam_links_df = pd.read_csv(r'data/steam-games/steam_support_info.csv')

# dictionary where key is app ID and value is name of game
steam_id_to_name = dict()

# dictionary where key is name and value is app ID of game
steam_name_to_id = dict()

# dictionary where key is app ID and value is name of game
steam_id_to_name = dict()

# dictionary where key is name and value is app ID of game
steam_name_to_id = dict()

# dictionary where key is app ID and value is index in steam_df
steam_id_to_idx = dict()

for i in range(len(steam_df['appid'])):
    steam_id_to_name[steam_df['appid'][i]] = steam_df['name'][i]
    steam_name_to_id[steam_df['name'][i]] = steam_df['appid'][i]
    steam_id_to_idx[steam_df['appid'][i]] = i

'''
FUNCTIONS
'''

def steam_jaccard(appid1, appid2):
    '''
    returns Jaccard similarity score between appid1 and appid2
    '''
    # dictionary where key is app ID and value is set of genres
    steam_sets = dict()
    for i in range(len(steam_df['appid'])):
        steam_sets[steam_df['appid'][i]] = set(steam_df['genres'][i].split(';'))
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

    # inverted indices where key is term and value is (appid, term_count_in_description)
    inv_idx = dict()
    # key is appid and value is list of tokens
    tok_lists = dict()
    for i in range(len(steam_descriptions_df['steam_appid'])):
        text = re.sub(r'<[^<>]+>', '', steam_descriptions_df['detailed_description'][i].lower())
        tok_list = re.findall(r'[a-z]+', text)
        tok_lists[steam_descriptions_df['steam_appid'][i]] = tok_list
        doc_count = dict() # contains counts for each term in document i
        for token in tok_list:
            if token in doc_count:
                doc_count[token] += 1
            else:
                doc_count[token] = 1
        for key in doc_count:
            if key in inv_idx:
                inv_idx[key].append((steam_descriptions_df['steam_appid'][i], doc_count[key]))
            else:
                inv_idx[key] = [(steam_descriptions_df['steam_appid'][i], doc_count[key])]

    # dictionary where key is term and value is idf
    idf = dict()
    n_docs = len(steam_descriptions_df['steam_appid'])
    for term in inv_idx:
        df = len(inv_idx[term])
        if df >= 50 and df / n_docs <= 0.9:
            idf[term] = math.log2(n_docs / (df + 1))

    # norms[i] = the norm of description of game with appid i
    norms = dict()
    acc = 0
    for term in inv_idx:
        for doc_count in inv_idx[term]:
            doc_idx = doc_count[0]
            if term in idf:
                if doc_idx in norms:
                    norms[doc_idx] += (doc_count[1] * idf[term]) ** 2
                else:
                    norms[doc_idx] = (doc_count[1] * idf[term]) ** 2
    for appid in norms:
        norms[appid] = math.sqrt(norms[appid])

    tf = Counter(tok_lists[appid])
    doc_score_dict = dict()

    for token in tf:
        if token in idf:
            for d, c in inv_idx[token]:
                if d in doc_score_dict:
                    doc_score_dict[d] += tf[token] * c * (idf[token] ** 2)
                else:
                    doc_score_dict[d] = tf[token] * c * (idf[token] ** 2)

    result = list()

    for doc_id in doc_score_dict:
        if doc_id != appid:
            doc_score_dict[doc_id] /= norms[appid] * norms[doc_id]
            result.append((doc_id, doc_score_dict[doc_id]))

    result = sorted(result, key=lambda pair: (-pair[0], pair[1]))

    for steam_appid in steam_df['appid']:
        if steam_appid not in doc_score_dict and steam_appid != appid:
            result.append((steam_appid, 0))

    return result

def steam_sim_list(appid):
    '''
    returns tuple list of game app IDs and average of cosine and Jaccard similarity scores
    '''
    list_jaccard = sorted(steam_jaccard_list(appid), key=lambda pair: pair[0])
    list_cosine = sorted(steam_cossim_list(appid), key=lambda pair: pair[0])
    list_both = list()
    for i in range(len(list_jaccard)):
        list_both.append((list_jaccard[i][0], (list_jaccard[i][1] + list_cosine[i][1]) / 2))
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
    for appid, score in score_list:
        i = steam_id_to_idx[appid]
        if type(steam_links_df['website'][i]) == float:
            web = None
        else:
            web = steam_links_df['website'][i]
        result_list.append((score, steam_df['name'][i], steam_df['genres'][i].split(';'), \
            steam_df['platforms'][i].split(';'), steam_df['price'][i], \
            steam_media_df['header_image'][i], web))
    return sorted(result_list, key=lambda x: x[0], reverse=True)[:30]

'''
TESTING
'''

# print('jaccard')
# output_jaccard = steam_get_rankings(steam_jaccard_list(steam_df['appid'][0]))
# for i in range(30):
#     print(output_jaccard[i])

# print('cossim')
# output_cossim = steam_get_rankings(steam_cossim_list(1069460))
# for i in range(30):
#     print(output_cossim[i])

# print('sim')
# output_sim = steam_get_rankings(steam_sim_list(1069460))
# for i in range(30):
#     print(output_sim[i])

# print('boolean and jaccard')
# output_jaccard = steam_jaccard_list(steam_df['appid'][0])
# filtered_jaccard = steam_get_rankings(steam_bool_filter(output_jaccard, genres_in=['Casual']))
# for i in range(30):
#     print(filtered_jaccard[i])

# print('boolean and cossim')
# output_cossim = steam_cossim_list(steam_df['appid'][0])
# filtered_cossim = steam_get_rankings(steam_bool_filter(output_cossim, min_price=10))
# for i in range(30):
#     print(filtered_cossim[i])

# print('boolean and sim')
# output_sim = steam_sim_list(steam_df['appid'][0])
# filtered_sim = steam_get_rankings(steam_bool_filter(output_sim, min_price=10))
# for i in range(30):
#     print(filtered_sim[i])
