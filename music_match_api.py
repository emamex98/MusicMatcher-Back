#!flask/bin/python
import json
import os
import pandas as pd
import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort

load_dotenv('.env')

host=os.getenv("HOST_MM")
port=int(os.getenv("PORT_MM"))
dbname=os.getenv("DBNAME_MM")
user=os.getenv("USER_MM")
password=os.getenv("PASS_MM")

conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname)
cur = conn.cursor()

app = Flask(__name__)

#gets all users
@app.route('/users', methods=['GET'])
def get_users():
    users = pd.read_sql('select * from User;', con=conn).to_json(orient='records')
    return users

# get user profile
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    query = 'select * from User where userId='+str(user_id)+';'
    user = pd.read_sql(query, con=conn).to_json(orient='records')
    return user

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
    return str(user_id), 201
    
# put to update spotify token
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_token(user_id):
    if not request.json:
        abort(400)
    query = 'UPDATE User SET spotifyToken = "'+request.json['spotify_token']+'" WHERE userId = '+str(user_id)+';'
    cur.execute(query)
    conn.commit()
    return str(user_id), 201

if __name__ == '__main__':
    app.run(debug=True) 
