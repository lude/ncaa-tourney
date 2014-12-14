from flask import Flask, request
from pymongo import MongoClient
import json
from bson import json_util
from bson.objectid import ObjectId

# Initialize the Flask application
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.ncaa_tourney

def jsonify(data):
    return json.dumps(data, default=json_util.default)

# This route will return a list in JSON format
@app.route('/games')
def games_list():
    return jsonify([game for game in db.games.find()])

@app.route('/winners', methods=['GET'])
def winners_list():
    return jsonify([game for game in db.winners.find()])

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
