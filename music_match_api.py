#!flask/bin/python
import json
from flask import Flask, jsonify, request, abort

data = None
with open('data.json') as file:
    data = json.load(file)

def write_json(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify({'users':data})

# get user profile
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({'user':data[user_id]})

# post to create user
@app.route('/user/create/', methods=['POST'])
def create_user():
    if not request.json:
        abort(400)
    user = {
        "user_id": data[-1]["user_id"]+1,
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
    data.append(user)
    write_json(data)
    return jsonify({'user':user}), 201
    
# put to update spotify token
@app.route('/user/update/<int:user_id>', methods=['PUT'])
def update_token(user_id):
    if not request.json:
        abort(400)
    data[user_id]['spotify_token'] = request.json.get('spotify_token',data[user_id]['spotify_token'])
    write_json(data)
    return jsonify({'user': data[user_id]})

if __name__ == '__main__':
    app.run(debug=True)