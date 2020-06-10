import json

genres = dict()
dataA = None
with open('top_artists.json') as file:
    dataA = json.load(file)

for item in dataA['items']:
    print(item['name'], item['id'], item['popularity'])
    for genre in item['genres']:
        if genre not in genres:
            genres[genre] = 1
        else:
            genres[genre] += 1

sort_orders = sorted(genres.items(), key=lambda x: x[1], reverse=True)
for i in range(3):
    print(sort_orders[i][0],sort_orders[i][1])

dataS = None
with open('top_songs.json') as file:
    dataS = json.load(file)

for item in dataS['items']:
    print(item['name'], item['id'],item['popularity'])