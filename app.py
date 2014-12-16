from flask import Flask, request
from pymongo import MongoClient
from pymongo import ASCENDING
from bson import json_util
from bson.objectid import ObjectId

import json

# Initialize the Flask application
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.ncaa_tourney

def jsonify(data):
    if isinstance(data, list):
        for item in data:
            item['id'] = str(item['_id'])
    elif isinstance(data, ObjectId):
        pass
    else:
        data['id'] = str(data['_id'])
    return json.dumps(data, default=json_util.default)

# This route will return a list in JSON format
@app.route('/games')
def games_list():
    return jsonify([game for game in db.games.find().sort("datetime",ASCENDING)])

@app.route('/winners/<oid>', methods=['GET'])
def winners_list(oid):
    return jsonify(
        db.winners.find_one({'_id':ObjectId(oid)})
    )

@app.route('/winners', methods=['POST'])
def winners_post():
    print(request.form)
    return jsonify(db.winners.save(request.get_json()))


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("6542"),
        debug=True
    )
