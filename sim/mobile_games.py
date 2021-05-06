import numpy as np
import pandas as pd
import re
import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

mobile_games_df_dict = {'App': str, 'Rating': np.float16, 'Type': str,
                        'Price': str, 'Content Rating': str, 'Genres': str, 'Web Link': str}
mobile_games_df = pd.read_csv(r'../data/mobile-games/googleplaystore.csv',
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
reviews_df = pd.read_csv(r'../data/mobile-games/user_reviews_cleaned.csv',
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
        include = True

        genres = set(mobile_games_df['Genres'][i].split(';'))
        if excluded_genres != None:
            for genre in excluded_genres:
                if genre in genres:
                    include = False
                    break
            if not include:
                continue

        if included_genres != None:
            for genre in included_genres:
                if genre not in genres:
                    include = False
                    break
            if not include:
                continue

        if min_price != None:
            price_str = mobile_games_df['Price'][i]
            price_str_list = price_str.split("$")
            price = 0
            if len(price_str_list) == 2:
                num_as_str = price_str_list[1]
                price = float(num_as_str)
            if price < min_price:
                continue

        if max_price != None:
            price_str = mobile_games_df['Price'][i]
            price_str_list = price_str.split("$")
            price = 0
            if len(price_str_list) == 2:
                num_as_str = price_str_list[1]
                price = float(num_as_str)
            if price > max_price:
                continue

        if min_rating != None:
            if int(mobile_games_df['Rating'][i]) < min_rating:
                continue

        filtered_games.append((game, score))

    return filtered_games


'''
SENTIMENT ANALYSIS
'''


def mgs_sentiment_list(score_list):
    sent_dict = dict()
    for game, score in score_list:
        if game in reviews_df['App']:
            i = reviews_df.index[reviews_df['App'] == game][0]
            sentiment = reviews_df['Sentiment'][i]
            if game in sent_dict:
                sent_dict[game].append(sentiment)
            else:
                sent_dict[game] = list()
                sent_dict[game].append(sentiment)
        else:
            sent_dict[game] = list()

    game_sent_mapping = dict()
    for game in sent_dict:
        game_sentiments = sent_dict[game]
        num_positives = game_sentiments.count("Positive")
        num_negatives = game_sentiments.count("Negative")
        if num_negatives == 0 or num_positives == 0:
            game_sent_mapping[game] = "Neutral"
        elif num_negatives == 0 and num_positives > 0:
            game_sent_mapping[game] = "Positive"
        elif (num_positives / num_negatives) >= 2.0:
            game_sent_mapping[game] = "Positive"
        elif num_positives == 0 and num_negatives > 0:
            game_sent_mapping[game] = "Negative"
        elif (num_negatives / num_positives) >= 2.0:
            game_sent_mapping[game] = "Negative"
        else:
            game_sent_mapping[game] = "Neutral"

    final_rankings = list()
    games_with_no_reviews = list()
    for game, score in score_list:
        if game in reviews_df['App']:
            if game_sent_mapping[game] == "Positive":
                final_rankings.append((game, score))
        else:
            games_with_no_reviews.append((game, score))
    for game, score in score_list:
        if game in reviews_df['App']:
            if game_sent_mapping[game] == "Neutral":
                final_rankings.append((game, score))
        else:
            games_with_no_reviews.append((game, score))
    for game, score in score_list:
        if game in reviews_df['App']:
            if game_sent_mapping[game] == "Negative":
                final_rankings.append((game, score))
        else:
            games_with_no_reviews.append((game, score))
    for game, score in games_with_no_reviews:
        final_rankings.append((game, score))

    return final_rankings


'''
SORT RANKINGS
'''


def mgs_get_rankings(score_list):
    score_list = mgs_sentiment_list(score_list)

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

        if (game, score, genres, rating, paid_or_free, content, web_link) not in result_list:
            result_list.append((game, score, genres, rating,
                                paid_or_free, content, web_link))

    result_list = sorted(result_list, key=lambda x: x[1], reverse=True)[:30]

    return result_list


'''
TESTS
'''

# print("\nQUERY: Helix")

# print("\nNON-FILTERED RESULTS:")
# j = mgs_jaccard_list('Helix')
# c = mgs_cossim_list('Helix')
# l = mgs_jacc_cossim(j, c)
# data1 = mgs_get_rankings(l)
# for i in range(len(data1)):
#     print(data1[i])

# print("\nFILTERED RESULTS:")
# filtered_l = mgs_boolean_filter(
#     l, included_genres=['Arcade'], excluded_genres=['Adventure'], max_price=1)
# data2 = mgs_get_rankings(filtered_l)
# for i in range(len(data2)):
#     print(data2[i])
