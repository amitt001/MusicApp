from math import sqrt
import pymongo
import pprint
# Returns a distance-based similarity score for person1 and person2

pp = pprint.PrettyPrinter()

try:
    conn=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e

db = conn['test'] 
#collection = db['user_ratings']

#critics = list(collection.find({}))
#pp.pprint (list(critics))
#critic_len = len(critics)
def correct_form(collection, person):#, person2):
    
    """
        function to convert the code into correct form
        correct form: dictionary with key as the song title
        and rating as value

        requires change iif data is not in form 
        {song1:rat1ing1, song2: rating2 ....}
    """
    #database call
    p = list(collection.find({'uID': person}))
    #p2 = list(collection.find({'uID': person2}))
    #creates a dict of form {song1: rating1, song2: rsting2...}
    pers = {p[x]['song'].keys()[-1]: p[x]['song'].values()[-1] for x in range(len(p))}
    #pers2 = {p2[x]['song'].keys()[-1]: p2[x]['song'].values()[-1] for x in range(len(p2))}
    return pers#[pers1, pers2]

def sim_distance(prefs,person1="7352910c889868df6d5f296fc3508d64955a0f26",person2="7352910c889868df6d5f296fc3508d64955a0f27"): 
    collection = db[prefs]
    #get in the required form
    pers1 = correct_form(collection, person1)
    pers2 = correct_form(collection, person2)

    si={}
    #collection name
    #creates users song rating dictionary
        
    for item in pers1:
        #pp.pprint(itemm)
        if item in pers2: 
            si[item]=1
    # if they have no ratings in common, return 0
    if len(si)==0: return 0
    # Add up the squares of all the differences
    #sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
    sum_of_squares=sum([pow(float(pers1[item])-float(pers2[item]),2) for item in pers1 if item in pers2])
    return 1/(1+sum_of_squares)


#############################
##Pearson Correlation Score##
#############################

def sim_pearson(prefs, p1="7352910c889868df6d5f296fc3508d64955a0f26", p2="7352910c889868df6d5f296fc3508d64955a0f27"):
    collection = db[prefs]
    #get in the required form
    p1 = correct_form(collection, p1)
    p2 = correct_form(collection, p2)
    #get the list of mutully rated item
    si = {}
    for item in p1:
	   if item in p2: si[item]=1

    n = len(si)

    if n == 0: return 0
    #since user ratings are in unicode format
    #converting to float
    for item in p1:
        p1[item] = float(p1[item])
    for item in p2:
        p2[item] = float(p2[item])

    # Add up all the preferences
    sum1=sum([p1[it] for it in si])
    sum2=sum([p2[it] for it in si])

    # Sum up the squares
    sum1Sq=sum([pow(p1[it],2) for it in si])
    sum2Sq=sum([pow(p2[it],2) for it in si])

    # Sum up the products
    pSum=sum([p1[it]*p2[it] for it in si])

    #calculate the pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r = num/den
    return r


#getting most similar critics to person

def topMatches(prefs, person, n=5, similarity=sim_pearson):

    """
    returns list of users with similarity score
    for ex:
        [(-0.15041420939904668, u'user1'), (0.45, u'user2'....)]
    """

    collection = db[prefs]
    data = list(collection.find({}, {'_id': 0}))
    #creates a list of users
    users = []
    for item in data:
        if item['uID'] not in users:
            users.append(item['uID'])

    scores=[(similarity(prefs, person, other), other) for other in users if other != person]

    #sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]


# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):

    """
    recommends top 5 songs/user to the given user/songs
    """

    collection = db[prefs]
    data = list(collection.find({}, {'_id': 0}))

    totals={}
    simSums={}
    #creates a list of users
    users = []
    for item in data:
        if item['uID'] not in users:
            users.append(item['uID'])

    for other in users:
        # don't compare me to myself
        if other==person: continue
        
        sim=similarity(prefs,person,other)
        # ignore scores of zero or lower
        if sim<=0: continue
        for item in correct_form(collection, other):
            #only score movies i haven't seen yet
            if item not in correct_form(collection, person) or correct_form(collection, other)[item]==0:
	        # Similarity * Score
                totals.setdefault(item,0)
                totals[item] += float(correct_form(collection, other)[item])*sim
                # Sum of similarities
	        simSums.setdefault(item,0)
	        simSums[item] += sim

        #create a normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            result[item][person] = prefs[person][item]

    return result

#########################################
##        Item-Based Filtering         ##
#########################################

def calculateSimilarItems(prefs, n=10):
    result={}
    itemprefs = transformPrefs(prefs)
    cnt = 0
    for item in itemprefs:
        cnt+=1
        if cnt%100 == 0: print('%d / %d' % (cnt, len(itemprefs)))

        #find the most similar items to this one
        scores = topMatches(itemprefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

#################################################
##Recommendations based on item-based filtering##
#################################################

def getRecommendedItems(prefs, itemMatch, user):
    userRatings=prefs[user]
    scores={}
    totalSim={}

    for (item, rating) in userRatings.items():
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRatings: continue

            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating

            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    rankings = [(score/totalSim[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

def make_songlist(prefs):

    """
    creates a text file with list of songs in it
    Not part of recommendations
    """

    collection = db[prefs]
    songs = collection.find({},{'_id' :0, 'song' :1})
    with open('songslist.txt', 'w') as sobj:
        for song in songs:
            sobj.write(song['song'].keys()[-1] + '\n')
