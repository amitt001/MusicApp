#!flask/bin/python
import os
import pprint
import hashlib
import json
from flask import Flask, jsonify, abort, make_response, request, url_for

import savedb
import ycrawl

app = Flask(__name__)
pp = pprint.PrettyPrinter()

@app.route('/')
def index():
    return 'Hello API!'

@app.route('/admin/<int:key>')    
def admin(key):

    """
        serious stuff going on
    """
    print("crawling")
    ycrawl.filereader("songslist.txt")
    print("binding links...")
    savedb.bind()
    print("forming recommendations...")
    savedb.formrec()

@app.route('/api/login', methods=['POST', 'GET'])
def login():
    with open('login.txt', 'a') as fobj:
        #data = str(request.json)
        #fobj.write(data)
        json.dump(request.json, fobj)
    #return '{"status": "ok", "code":"201"}'
    #request.json['']
    uhash = hashlib.sha1(request.json['user']).hexdigest()
    try:
        savedb.login(request.json['user'], uhash)
    except:
        pass

    with open('hashmap.txt', 'a') as hashobj:
        json.dump({request.json['user']: uhash}, hashobj)
        hashobj.write("\n")
    print request.json, uhash
    return uhash


@app.route('/api/songs/get/<string:task_id>', methods=['GET', 'POST'])
def get_songs_byid(task_id): #for each ID
    #sends songs on get request by client


    """
    ccreate a binding for song and youtube
    create list of top songs that changes as user listens
    """


    #data = savedb.get_data(task_id)
    #savedb.formrec()
    return jsonify(savedb.get_recommendations(task_id)[-1]['data'])
    atask = {}
    a = json.load(open('usersongs.txt'))
    atask.setdefault('songs', a)
    #return jsonify({'task': atask})
    return jsonify(atask)


@app.route('/api/songs/data', methods=['POST'])
def create_task():
    
    """receives the songs data by user"""

    if not request.json: #or not 'title' in request.json:
        abort(400)
    #print request.json

    with open('usersongs.txt', 'w') as fobj:#later chnage it to append
        #data = str(request.json)
        #fobj.write(data)
        json.dump(request.json, fobj)
        fobj.write("\n")
    #print request.json.values()
    #pp.pprint(request.json)
    postdata = {x for x in request.json}
    savedb.usersongs(request.json.keys()[0], json.loads(request.json.values()[0]))

    return '{"status": "ok", "code":"201"}'


@app.route('/api/songs/rate', methods=['POST'])
def ratesongs():
    if not request.json: #or not 'title' in request.json:
        abort(400)
    with open('ratings.txt', 'a') as fobj:
        #data = str(request.json)
        #fobj.write(data)
        json.dump(request.json, fobj)
        fobj.write("\n")
        #fobj.write("\n")
    print request.json
    savedb.rate(request.json)
    return '{"status": "ok", "code":"201"}'












@app.errorhandler(404)#when data doens't exists in our db
def not_found(error):#instead of an html error we are generating json
    return make_response(jsonify({'error': 'Not Found'}), 404)



if __name__ == '__main__':
#    port = int(os.environ.get("POST", 5000)
    app.run(host='0.0.0.0', port=5000, debug=True)
