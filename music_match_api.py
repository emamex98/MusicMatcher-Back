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

#@app.route('/user/<int:user_id>/match', methods=['POST'])
#def post_user_match(user_id):




"""
POST

post_top_artist
post_top_track

GET

get_top_artist
get_top_track
"""

if __name__ == '__main__':
    app.run(debug=True) 
