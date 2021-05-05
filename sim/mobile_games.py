import numpy as np
import pandas as pd
import re
import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

mobile_games_df_dict = {'App': str, 'Rating': np.float16, 'Type': str,
                        'Price': str, 'Content Rating': str, 'Genres': str, 'Web Link': str}
mobile_games_df = pd.read_csv(r'data/mobile-games/googleplaystore.csv',
                              usecols=mobile_games_df_dict, dtype=mobile_games_df_dict)


'''
JACCARD SIMILARITY
'''

mgs_sets = dict()
for i in range(len(mobile_games_df['App'])):
    key = mobile_games_df['App'][i]
    app_type = mobile_games_df['Type'][i]
    content = mobile_games_df['Content Rating'][i]
    genres = mobile_games_df['Genres'][i].split(';')
    mgs_sets[key] = set([app_type, content] + genres)


def mgs_jaccard(app1, app2):
    A_int_B = mgs_sets[app1].intersection(mgs_sets[app2])
    A_uni_B = mgs_sets[app1].union(mgs_sets[app2])
    return len(A_int_B) / len(A_uni_B)


def mgs_jaccard_list(app):
    score_list = []
    for app_name in mobile_games_df['App']:
        if app_name != app:
            score_list.append((app_name, mgs_jaccard(app, app_name)))
    sorted(score_list, key=lambda x: x[1], reverse=True)
    return score_list


'''
COSINE SIMILARITY
'''

reviews_dict = {'App': str, 'Translated_Review': str}
reviews_df = pd.read_csv(r'data/mobile-games/user_reviews_cleaned.csv',
                         usecols=reviews_dict, dtype=reviews_dict).dropna()
reviews_df = reviews_df.groupby('App')['Translated_Review'].apply(
    ';'.join).reset_index()

tfidf_vec = TfidfVectorizer(stop_words="english")
tfidf_mat = tfidf_vec.fit_transform(reviews_df['Translated_Review'])


def mgs_cossim_list(app):
    if reviews_df['App'][reviews_df['App'] == app].count() > 0:
        idx = reviews_df.index[reviews_df['App'] == app][0]
        query_tfidf = tfidf_vec.transform(
            [str(reviews_df['Translated_Review'][idx])])
        cossims = cosine_similarity(query_tfidf, tfidf_mat).flatten()
        result = list()
        for i in range(len(cossims)):
            if i != idx:
                result.append((reviews_df['App'][i], cossims[i]))
        return result
    return None


'''
COMBINE JACCARD AND COSINE SIMILARITY
'''


def mgs_jacc_cossim(jacc_list, cossim_list):
    if cossim_list == None:
        return jacc_list

    avg_dict = dict()

    for game, j_score in jacc_list:
        avg_dict[game] = j_score / 2

    for game, c_score in cossim_list:
        if game in avg_dict:
            avg_dict[game] += c_score / 2

    final_score_list = []
    for game in avg_dict:
        score = avg_dict[game]
        final_score_list.append((game, score))

    final_score_list.sort(key=lambda x: x[1], reverse=True)
    return final_score_list


'''
BOOLEAN SEARCH
'''


def mgs_boolean_filter(score_list, included_genres=None, excluded_genres=None,
                       max_price=None, min_price=None, min_rating=None):
    filtered_games = []

    for (game, score) in score_list:
        i = mobile_games_df.index[mobile_games_df['App'] == game][0]

        if included_genres != None and excluded_genres != None:
            genres = mobile_games_df['Genres'][i].split(';')
            for g in genres:
                if g not in included_genres or g in excluded_genres:
                    continue
        elif included_genres != None and excluded_genres == None:
            genres = mobile_games_df['Genres'][i].split(';')
            for g in genres:
                if g not in included_genres:
                    continue
        elif excluded_genres != None and included_genres == None:
            genres = mobile_games_df['Genres'][i].split(';')
            for g in genres:
                if g in excluded_genres:
                    continue

        if min_price != None or max_price != None:
            price_str = mobile_games_df['Price'][i]
            if len(price_str) == 1:
                price = 0
            else:
                price = float(price(str[1:]))

            if min_price != None and price < min_price:
                continue
            if max_price != None and price > max_price:
                continue

        if min_rating != None:
            rating = float(mobile_games_df['Rating'][i])
            if rating < min_rating:
                continue

        filtered_games.append(game)

    return filtered_games


'''
SORT RANKINGS
'''


def mgs_get_rankings(score_list):
    result_list = list()

    for game, score in score_list:
        i = mobile_games_df.index[mobile_games_df['App'] == game][0]

        genres = mobile_games_df['Genres'][i].split(';')
        rating = mobile_games_df['Rating'][i]
        paid_or_free = mobile_games_df['Type'][i]
        content = mobile_games_df['Content Rating'][i]

        web_link = str()
        if type(mobile_games_df['Web Link'][i]) != None:
            web_link = mobile_games_df['Web Link'][i]

        result_list.append(game, score, genres, rating,
                           paid_or_free, content, web_link)

    result_list = sorted(result_list, key=lambda x: x[1], reverse=True)[:30]
    return result_list


# j = mgs_jaccard_list('Helix')
# print(j)
# c = mgs_cossim_list('Helix')
# print(c)
# l = mgs_jacc_cossim(j, c)
# data = mgs_get_rankings(l)
# print(data)

# test_app1 = mobile_games_df['App'][0]
# print("\nQuery: " + test_app1)

# print('Jaccard Similarity:')
# jaccard_scores = mgs_jaccard_list(test_app1)
# output_jaccard = mgs_get_rankings(jaccard_scores)
# for i in range(50):
#     print(output_jaccard[i])

# test_app2 = reviews_df['App'][0]
# print("\nQuery: " + test_app2)
# print('Cosine Similarity:')
# output_cossim = mgs_cossim_list(test_app2)
# for i in range(len(output_cossim)):
#     print(output_cossim[i])

# all_games_list = list(app_set)
# test_app = all_games_list[3]
# output_jacc2 = mgs_jaccard_list(test_app)
# output_cossim2 = mgs_cossim_list(test_app)
# final_score_list = mgs_jacc_cossim(output_jacc2, output_cossim2)

# print("\nQUERY: " + test_app)
# print("\n")
# print('Final Similarity Scores:')
# for i in range(50):
#     print(final_score_list[i])

# print("\nFILTERED RESULTS")
# filtered_results = mgs_boolean_filter(
#     final_score_list, ['Strategy'], ['Adventure'])
# for i in range(50):
#     print(filtered_results[i])

# result = mgs_get_rankings(final_score_list)
# for i in range(len(result)):
#     print(result[i])
#     print("\n")
