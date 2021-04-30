import pandas as pd
import re
import csv


mgs = pd.read_csv(r'data/mobile-games/googleplaystore.csv')

app_categories = mgs['Category']
booleans = []
for cat in app_categories:
    if not re.search('GAME', cat):
        booleans.append(False)
    else:
        booleans.append(True)
Filtered = pd.Series(booleans)
game_apps = (mgs[Filtered]).reset_index(drop=True)

games = game_apps['App']
games_set = set(games)


reviews = pd.read_csv(r'data/mobile-games/googleplaystore_user_reviews.csv')
reviews = (reviews.dropna()).reset_index(drop=True)
app_names = reviews['App']

relevant_apps = list()
for game in games_set:
    for app in app_names:
        if app == game:
            relevant_apps.append(app)

with open('data/mobile-games/googleplaystore_user_reviews.csv', 'r') as inp, \
        open('data/mobile-games/user_reviews_cleaned.csv', 'w') as out:
    writer = csv.writer(out)
    for row in csv.reader(inp):
        if row[0] in relevant_apps:
            writer.writerow(row)

print("Write Successful")
