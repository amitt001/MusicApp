import pymongo
import json
import pprint

import recommendations as reco

from bson.objectid import ObjectId

pp = pprint.PrettyPrinter()

try:
    conn=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e

#db = connection['MusicApp']
db = conn['test']


def login(_id, uhash):
    collection = db['user_login']
    collection.insert({'_id' : _id, 'hash' : uhash})
    print(list(collection.find()))


def usersongs(_id, data):
    collection = db['user_songs']
    collection.save({'_id' : _id, 'data' : data})
    #print (list(collection.find()))


def rate(data):
    collection = db['user_ratings']
    col = list(collection.find({'mID' : data['mID'], 'uID' : data['uID']}))
    #if already rated in past add new
    if col:
        data['_id'] = col[0]['_id']
        print data

    collection.save(data)


def bind():
    
    """
    binds songs name to their youtube links
    """
    collection = db["song_link"]
    with open("utubesongs", 'r') as uobj:
        data = json.load(uobj)
        for k,v in data.items():
            collection.save({'_id': k.strip(), 'url': v.strip()})
    pp.pprint(list(collection.find()))

       
def get_data(_id):
    """
    get ratings data of ratings, useless?????????
    """
    collection = db['user_ratings']
    data = list(collection.find({'uID': _id}, {'_id': 0}))
    return data


def formrec():

    """
        crates recommendations for user

    """

    collection = db['user_ratings']
    linkcollection = db['song_link']
    newcollection = db['user_recommendations']

    master = {}
    rec_list = list(collection.distinct('uID'))
    #when empty ie no similar user or recommendations
    if not rec_list:
        defcollection = db['song_default']
        master['songs'] = ""
        return master

    for user in rec_list:
        tempdict = {}
        tempdict.setdefault(user, [])
        udata = reco.getRecommendations(reco.master, user)
        for data in udata:
            try:
                tempdict[user].append((list(linkcollection.find({'_id': data[1]}))[-1]))
            except IndexError:
                pass
        #print user
        master['songs'] = tempdict
        #pp.pprint(master)
        newcollection.save({'_id': user, 'data': master})

    #pp.pprint(list(newcollection.find()))
        #newcollection.save({'_id': user, 'songs' : reco.getRecommendations(reco.master, user)})
    #print reco.getRecommendations(reco.master, list(collection.distinct('uID'))[-1])


def get_recommendations(_id):
    collection = db['user_recommendations']
    return list(collection.find({'_id':_id}, {'_id':0}))