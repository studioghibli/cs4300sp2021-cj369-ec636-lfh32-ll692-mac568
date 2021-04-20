import pandas as pd
import re
import math
from collections import Counter

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


# compute tf-idf vectors and cossim

reviews = pd.read_csv(r'data/mobile-games/googleplaystore_user_reviews.csv')
reviews = (reviews.dropna()).reset_index(drop=True)
reviews = reviews.head(1000)
# print("the length of reviews is " + str(len(reviews)))


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
    # for tup in inv_idx[term]:
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


def mgs_cossim_list(app):
    '''
    returns sorted list of most similar games to appid based on cosine similarity
    '''
    tf = Counter(
        tok_lists[app])  # dict for the number of times each word appears in all the apps
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
            cossim.append((app_score_dict[app_name], app_name))

    result = sorted(cossim, key=lambda pair: (-pair[0], pair[1]))

    for app_name in app_set:
        if app_name not in app_score_dict and app_name != app:
            cossim.append((0, app_name))

    return cossim


def mgs_get_rankings(score_list):
    return sorted(score_list, key=lambda x: x[1], reverse=True)


# test_app1 = game_apps['App'][0]
# print("Query: " + game_apps['App'][0])

# print('\nJaccard Similarity:')
# jaccard_scores = mgs_jaccard_list(test_app1)
# output_jaccard = mgs_get_rankings(jaccard_scores)
# for i in range(50):
#     print(output_jaccard[i])


# test_app2 = reviews['App'][0]

# print('\nCosine Similarity:')
# output_cossim = mgs_cossim_list(test_app2)
# for i in range(len(output_cossim)):
#     print(output_cossim[i])