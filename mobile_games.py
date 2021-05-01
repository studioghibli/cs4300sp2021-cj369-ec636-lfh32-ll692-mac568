import pandas as pd
import re
import math
from collections import Counter

# make the dataset usable

mgs = pd.read_csv(r'data/mobile-games/googleplaystore.csv')

app_categories = mgs['Category']
booleans = []
for cat in app_categories:
    if not re.search('GAME', cat):
        booleans.append(False)
    else:
        booleans.append(True)

Filtered = pd.Series(booleans)
game_apps = mgs[Filtered]
game_apps = game_apps.reset_index(drop=True)

# code for jaccard

mgs_sets = dict()
for i in range(len(game_apps['App'])):
    key = game_apps['App'][i]
    app_type = game_apps['Type'][i]
    content = game_apps['Content Rating'][i]
    genres = game_apps['Genres'][i].split(';')
    mgs_sets[key] = set(app_type) | set(content) | set(genres)


def mgs_jaccard(app1, app2):
    A_int_B = mgs_sets[app1].intersection(mgs_sets[app2])
    A_uni_B = mgs_sets[app1].union(mgs_sets[app2])
    return len(A_int_B) / len(A_uni_B)


def mgs_jaccard_list(app):
    score_list = []
    for app_name in game_apps['App']:
        if app_name != app:
            score_list.append((app_name, mgs_jaccard(app, app_name)))
    return score_list


def mgs_get_rankings(score_list):
    return sorted(score_list, key=lambda x: x[1], reverse=True)

# code for cossim


reviews = pd.read_csv(r'data/mobile-games/user_reviews_cleaned.csv')
reviews = (reviews.dropna()).reset_index(drop=True)


def tokenize(text):
    return [x for x in re.findall(r"[a-z]+", text.lower())]


app_set = set(reviews['App'])
N = len(app_set)

tok_lists = dict()
for app in app_set:
    for j in range(len(reviews['App'])):
        app_name = reviews['App'][j]
        if app == app_name:
            rev = reviews['Translated_Review'][j]
            tokenized_review = tokenize(rev)
            if app in tok_lists:
                tok_lists[app] = tok_lists[app] + tokenized_review
            else:
                tok_lists[app] = tokenized_review

def mgs_cossim_list(app):
    '''
    returns sorted list of most similar games to appid based on cosine similarity
    '''
    inv_idx = dict()
    for app in app_set:
        tokens = tok_lists[app]
        token_set = set(tokens)
        for term in token_set:
            tf = tokens.count(term)
            inv_idx[term] = (app, tf)

    idf_dict = dict()
    for term in inv_idx:
        df = len(inv_idx[term])
        if df >= 50 and df / N <= 0.9:
            idf[term] = math.log2(N / (df + 1))

    norms_dict = dict()
    acc = 0
    for term in inv_idx:
        tup = inv_idx[term]
        app_name = tup[0]
        tf = tup[1]
        if term in idf_dict:
            idf = idf_dict[term]
            if app_name in norms:
                norms[app_name] += (tf * idf) ** 2
            else:
                norms[doc_idx] = (tf * idf) ** 2
    for app in norms_dict:
        norms_dict[app] = math.sqrt(norms_dict[app])

    tf = Counter(tok_lists[app])
    app_score_dict = dict()

    for token in tf:
        if token in idf_dict:
            for app_name, count in inv_idx[token]:
                if app_name in app_score_dict:
                    app_score_dict[d] += tf[token] * \
                        count * (idf_dict[token] ** 2)
                else:
                    app_score_dict[d] = tf[token] * \
                        count * (idf_dict[token] ** 2)

    cossim = list()

    for app_name in app_score_dict:
        if app_name != app:
            app_score_dict[app_name] = app_score_dict[app_name] / \
                (norms_dict[app] * norms_dict[app_name])
            cossim.append((app_name, app_score_dict[app_name]))

    result = sorted(cossim, key=lambda pair: (-pair[0], pair[1]))

    for app_name in app_set:
        if app_name not in app_score_dict and app_name != app:
            cossim.append((app_name, 0))

    return cossim


# code for combining jaccard and cossim

def mgs_jacc_cossim(jacc_list, cossim_list):
    avg_dict = dict()

    for tup in jacc_list:
        game = tup[0]
        score = tup[1]
        avg_dict[game] = score

    for tup in cossim_list:
        game = tup[0]
        score = tup[1]
        avg_dict[game] = (avg_dict[game] + score) / 2

    final_score_list = []
    for game in avg_dict:
        score = avg_dict[game]
        final_score_list.append((game, score))

    final_score_list.sort(key=lambda x: x[1], reverse=True)

    return final_score_list


# dictionary where key is name and value is index of game in dataset
mgs_name_to_idx = dict()

for i in range(len(game_apps['App'])):
    app_name = game_apps['App'][i]
    mgs_name_to_idx[app_name] = i


def mgs_boolean_genre(score_list, included_genres, excluded_genres):
    filtered_games = []

    for i in range(len(game_apps['App'])):
        genres = game_apps['Genres'][i].split(';')
        for g in genres:
            if g in included_genres and g not in excluded_genres:
                game = game_apps['App'][i]
                filtered_games.append(game)

    return filtered_games


def mgs_boolean_price(score_list, included_price):
    filtered_games = []

    for i in range(len(game_apps['App'])):
        price_str = game_apps['Price'][i]
        price_str_list = price.split("$")
        price = 0
        if len(price_str_list) == 2:
            price = float(price_str_list[1])
        if price <= included_price:
            game = game_apps['App'][i]
            filtered_games.append(game)

    return filtered_games


def mgs_boolean_rating(score_list, included_rating):
    filtered_games = []

    for i in range(len(game_apps['App'])):
        rating = float(game_apps['Rating'][i])
        if rating >= included_rating:
            game = game_apps['App'][i]
            filtered_games.append(game)

    return filtered_games


def mgs_boolean_filter(score_list, included_genres=None, excluded_genres=None,
                       included_price=None, included_rating=None):
    filtered_games = []

    for (game, score) in score_list:
        i = mgs_name_to_idx[game]

        if included_genres != None and excluded_genres != None:
            genres = game_apps['Genres'][i].split(';')
            for g in genres:
                if not (g in included_genres and g not in excluded_genres):
                    continue
        elif included_genres != None and excluded_genres == None:
            genres = game_apps['Genres'][i].split(';')
            for g in genres:
                if g not in included_genres:
                    continue
        elif excluded_genres != None and included_genres == None:
            genres = game_apps['Genres'][i].split(';')
            for g in genres:
                if g in excluded_genres:
                    continue

        if included_price != None:
            price_str = game_apps['Price'][i]
            price_str_list = price.split("$")
            price = 0
            if len(price_str_list) == 2:
                price = float(price_str_list[1])
            if not price <= included_price:
                continue

        rating = int()
        if included_rating != None:
            rating = float(game_apps['Rating'][i])
            if not rating >= included_rating:
                continue

        filtered_games.append(game)

    return filtered_games


# test_app1 = game_apps['App'][0]
# print("\nQuery: " + test_app1)

# print('Jaccard Similarity:')
# jaccard_scores = mgs_jaccard_list(test_app1)
# output_jaccard = mgs_get_rankings(jaccard_scores)
# for i in range(50):
#     print(output_jaccard[i])


# test_app2 = reviews['App'][0]

# print("\nQuery: " + test_app2)
# print('Cosine Similarity:')
# output_cossim = mgs_cossim_list(test_app2)
# for i in range(len(output_cossim)):
#     print(output_cossim[i])

# all_games_list = list(app_set)
# test_app3 = all_games_list[3]
# jacc2 = mgs_jaccard_list(test_app3)
# output_jacc2 = mgs_get_rankings(jacc2)
# output_cossim2 = mgs_cossim_list(test_app3)
# final_score_list = mgs_jacc_cossim(output_jacc2, output_cossim2)

# print("\nQuery: " + test_app3)
# print('Final Similarity Scores:')
# for i in range(50):
#     print(final_score_list[i])

# print("\nFILTERED RESULTS")
# filtered_results = mgs_boolean_filter(final_score_list, ['Strategy'])
# for i in range(50):
#     print(filtered_results[i])
