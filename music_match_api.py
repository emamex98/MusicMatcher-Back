#!flask/bin/python
import json
import os
import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort

load_dotenv('.env')

host=os.getenv("HOST_MM")
port=int(os.getenv("PORT_MM"))
dbname=os.getenv("DBNAME_MM")
user=os.getenv("USER_MM")
password=os.getenv("PASS_MM")

conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname, cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

app = Flask(__name__)

def checkPreference(candidates, user_id):
    query = 'SELECT genderInterest, minAgeInterest, maxAgeInterest From User WHERE userId='+str(user_id)+';'
    cur.execute(query)
    userInfo = cur.fetchall()
    
    if not userInfo["genderInterest"]:
        return candidates

    for candidate in candidates:
        query = 'SELECT genderInterest, minAgeInterest, maxAgeInterest From User WHERE userId='+str(candidate)+';'
        cur.execute(query)
        userCandidate = cur.fetchall()
        if not userCan["gender"]:
            continue 
        if userCandidate["gender"]!=userInfo["genderInterest"]:
            del candidates[candidate]
    return candidate
    

def topArtistsTable():
    #Save table TopArtists to dict
    query = 'SELECT * FROM TopArtists;'
    cur.execute(query)
    topArtists = cur.fetchall()
    return topArtists

def topTracksTable():
    #Save table TopTracks to dict
    query = 'SELECT * FROM TopTracks;'
    cur.execute(query)
    topTracks = cur.fetchall()
    return topTracks

def topGenresTable():
    #Save table TopGenres to dict
    query = 'SELECT * FROM TopGenres;'
    cur.execute(query)
    topGenres = cur.fetchall()
    return topGenres

def matchTracks(user_id):
    trackTable = topTracksTable()
    tracksSet = dict()
    # {"song": {user1, user2, user3}}
    for item in trackTable:
        if item['trackId'] not in tracksSet:
            tracksSet[item['trackId']] = set()
        tracksSet[item['trackId']].add(item['userId'])
    #{user2: 0, }
    candidates = dict()

    for track in tracksSet:
        if user_id in tracksSet[track]:
            tracksSet[track].remove(user_id)
            for user in tracksSet[track]:
                if user not in candidates:
                    candidates[user]= []
                candidates[user].append(track)
    
    for candidate in candidates:
        if len(candidates.get(candidate))<3:
            del candidates[candidate]
    return candidates
                
def insertMatchByTrack(user_id, candidate):
    matchId = None
    querySelect = 'SELECT macthId, userA, userB FROM Match WHERE (userA='+str(user_id)+' AND userB='+str(candidate)+') OR (userA='+str(candidate)+' AND userB='+str(user_id)+');'
    cur.execute(querySelect)
    exists = cur.fetchall()
    if exists:
        matchId = exists["matchId"]
    else:
        queryInsert = 'INSERT INTO Match (userA, userB, isUnmatched) VALUES ('+str(user_id)+','+str(candidate)+',false);'
        cur.execute(queryInsert)
        #conn.commit()
        matchId = cur.lastrowid
    return matchId

def insertMatchedTrack(macthId, trackId):
    querySelect = 'SELECT matchId, trackId FROM MatchedTrack WHERE (matchId='+str(macthId)+' AND trackId="'+trackId+'");'
    cur.execute(querySelect)
    exists = cur.fetchall()
    if exists:
        return
    queryInsert = 'INSERT INTO MatchedTrack (matchId, trackId) VALUES ('+str(macthId)+',"'+trackId+'");'
    cur.execute(queryInsert)
    #conn.commit()

#gets all users
@app.route('/users', methods=['GET'])
def get_users():
    query = 'select * from User;'
    cur.execute(query)
    result = cur.fetchall()
    return jsonify({"users":result})

# get user profile
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    query = 'select * from User where userId='+str(user_id)+';'
    cur.execute(query)
    result = cur.fetchall()
    return jsonify({"user":result})

# post to create user
@app.route('/user/create/', methods=['POST'])
def create_user():
    if not request.json:
        abort(400)
    user = {
        "name": request.json['name'],
        "email": request.json['email'],
        "gender": request.json.get('gender', ""),
        "age": request.json['age'],
        "city": request.json['city'],
        "gender_interest": request.json.get('gender_interest', ""),
        "min_age_interest": request.json.get('min_age_interest', 18),
        "max_age_interest": request.json.get('max_age_interest', request.json['age']*2),
        "limit_range_distance": request.json.get('limit_range_distance', 10),
        "spotify_token": ""
    }
    query = 'INSERT INTO User (name,email,gender,age,city,genderInterest,minAgeInterest,maxAgeInterest,limitRangeDistance,spotifyToken) VALUES ("'+user["name"]+'","'+user["email"]+'","'+user["gender"]+'",'+str(user["age"])+',"'+user["city"]+'","'+user["gender_interest"]+'",'+str(user["min_age_interest"])+','+str(user["max_age_interest"])+','+str(user["limit_range_distance"])+',"'+user["spotify_token"]+'");'
    cur.execute(query)
    user_id = cur.lastrowid
    conn.commit()
    result = jsonify({"user_id":user_id})
    return result, 201
    
# put to update spotify token
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_token(user_id):
    if not request.json:
        abort(400)
    query = 'UPDATE User SET spotifyToken = "'+request.json['spotify_token']+'" WHERE userId = '+str(user_id)+';'
    cur.execute(query)
    conn.commit()
    result = jsonify({"user_id":user_id})
    return result, 201

# post users top tracks
@app.route('/user/<int:user_id>/top_tracks', methods=['POST'])
def post_top_track(user_id):
    if not request.json:
        abort(400)
    for item in request.json['items']:
        query = 'INSERT INTO TopTracks (trackId, userId, ranking) VALUES ("'+item['id']+'",'+str(user_id)+','+str(item['popularity'])+');'
        cur.execute(query)
        conn.commit()
    return jsonify({"user_id":user_id}),201

# get users top tracks
@app.route('/user/<int:user_id>/top_tracks', methods=['GET'])
def get_top_track(user_id):
    query = 'SELECT trackId, ranking From TopTracks WHERE userId='+str(user_id)+';'
    cur.execute(query)
    results = cur.fetchall()
    return jsonify({"users":results})

# post users top artists and genres
@app.route('/user/<int:user_id>/top_artists', methods=['POST'])
def post_top_artist(user_id):
    if not request.json:
        abort(400)
    genres = dict()
    for item in request.json['items']:
        query = 'INSERT INTO TopArtists (artistId, userId, ranking) VALUES ("'+item['id']+'",'+str(user_id)+','+str(item['popularity'])+');'
        cur.execute(query)
        conn.commit()
        for genre in item['genres']:
            if genre not in genres:
                genres[genre] = 1
            else:
                genres[genre] += 1
    sort_orders = sorted(genres.items(), key=lambda x: x[1], reverse=True)
    for i in range(len(sort_orders)):
        query = 'INSERT INTO TopGenres (genreId, userId, ranking) VALUES ("'+sort_orders[i][0]+'",'+str(user_id)+','+str(i+1)+');'
        cur.execute(query)
        conn.commit()
    return jsonify({"user_id":user_id}),201

# get users top artists and genres
@app.route('/user/<int:user_id>/top_artists', methods=['GET'])
def get_top_artist(user_id):
    query = 'SELECT artistId, ranking From TopArtists WHERE userId='+str(user_id)+';'
    cur.execute(query)
    results = cur.fetchall()
    return jsonify({"users":results})

# get users top genres
@app.route('/user/<int:user_id>/top_genres', methods=['GET'])
def get_top_genre(user_id):
    query = 'SELECT genreId, ranking From TopGenres WHERE userId='+str(user_id)+';'
    cur.execute(query)
    results = cur.fetchall()
    return jsonify({"users":results})

# post user match track
@app.route('/user/<int:user_id>/match_track', methods=['POST'])
def post_user_match_track(user_id):
    candidates = matchTracks(user_id)

    for candidate in candidates:
        matchId = insertMatchByTrack(user_id, candidate)
        for track in candidates[candidate]:
            insertMatchedTrack(matchId, track)

    return jsonify({"user_id":user_id}),201

# get all matches for a user
@app.route('/user/<int:user_id>/match', methods=['GET'])
def get_user_match(user_id):
    query = 'SELECT * FROM Match WHERE userA='+str(user_id)+' OR userB='+str(user_id)+';'
    cur.execute(query)
    results = cur.fetchall()
    return jsonify({"users":results})

# put unmatch user
@app.rout('/user/<int:user_id>/match', methods=['PUT'])
def put_user_unmatch(user_id):
    if not request.json:
        abort(400)
    query = 'UPDATE User SET isUnmatched = true WHERE (userA = '+str(user_id)+' AND userB='+str(request.json['otherUser'])+') OR (userA='+str(request.json['otherUser'])+' AND userB='+str(user_id)+');'
    cur.execute(query)
    conn.commit()
    result = jsonify({"user_id":user_id})
    return result, 201



"""
POST

post_top_artist
post_top_track

GET

get_top_artist
get_top_track
"""

if __name__ == '__main__':
    #print(topGenresTable())
    app.run(debug=True) 
    
