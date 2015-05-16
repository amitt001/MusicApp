from math import sqrt
# Returns a distance-based similarity score for person1 and person2
import pymongo
import pprint
# Returns a distance-based similarity score for person1 and person2

pp = pprint.PrettyPrinter()

try:
    conn=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e
import json
db = conn['test'] 


collection = db['user_ratings']
data = list(collection.find({}, {'_id': 0}))
#get user list
users = []
for item in data:
    if item['uID'] not in users:
        users.append(item['uID'])
#creates on master dict that contains nested dict of user and song ratings and song
master = {}
for user in users:
    udat = list(collection.find({'uID': user}, {'_id': 0}))
    k = {dat['song'].keys()[-1] : dat['song'].values()[-1] for dat in udat}
    master[user] = k
#convert unicode rating to float for mathematical ops
for ky,val in master.items(): 
    for inky, inval in val.items():
        master[ky][inky] = float(master[ky][inky])


def sim_distance(prefs,person1,person2): 
###############################
##Eucladians Distance Metric###
###############################
# Get the list of shared_items
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]: 
            si[item]=1
    # if they have no ratings in common, return 0
    if len(si)==0: return 0
    # Add up the squares of all the differences
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])

    return 1/(1+sum_of_squares)


#############################
##Pearson Correlation Score##
#############################

def sim_pearson(prefs, p1, p2):
    #get the list of mutully rated item
    si = {}
    for item in prefs[p1]:
	if item in prefs[p2]: si[item]=1

    n = len(si)

    if n == 0: return 0

    # Add up all the preferences
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])

    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])

    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])

    #calculate the pearson score
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r = num/den
    return r


#getting most similar critics to person

def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores=[(similarity(prefs, person, other), other) for other in prefs if other != person]

    #sort the list so the highest scores appear at the top
    scores.sort()
    scores.reverse()
    return scores[0:n]


# Gets recommendations for a person by using a weighted average
# of every other user's rankings
def getRecommendations(prefs,person,similarity=sim_pearson):
    totals={}
    simSums={}
    
    for other in prefs:
        # don't compare me to myself
        if other==person: continue
        
        sim=similarity(prefs,person,other)

	# ignore scores of zero or lower
	if sim<=0: continue
	for item in prefs[other]:
            #only score movies i haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
	        # Similarity * Score
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                # Sum of similarities
	        simSums.setdefault(item,0)
	        simSums[item]+=sim

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