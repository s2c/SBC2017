import numpy as np
import random
import scipy
import pandas as pd
import warnings
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AffinityPropagation
import paho.mqtt.client as mqtt



def main():
	dataPath = 'data/'
	users = dataPath + 'users.csv'
	loc = dataPath + 'rest.csv'
	est = dataPath + 'est.csv'
	# ads = dataPath + 'ads.csv'

	#converts a column to categorical data
	def convertCategorical(df,colName):
	    return df[colName].astype('category').cat.codes # replace gender by a code
	    # read and sanitize users
	usersDF = pd.read_csv(users)
	usersDF = usersDF.drop('Name',1) #Name is useless when aggregating, and is already replaced by a number
	usersDF.employment = convertCategorical(usersDF,"employment")# replace employment by a code
	usersDF.Gender = convertCategorical(usersDF,"Gender")# replace gendar by a code
	# usersDF

	# Read last check ins
	checksDF = pd.read_csv(loc,header=0)
	checksDF = checksDF.drop('unknown',1)
	checksDF = checksDF.drop('date',1)
	checksDF = checksDF.drop('time',1)
	checksDF.day = convertCategorical(checksDF,'day')
	checksDF.location = convertCategorical(checksDF,'location')
	# checksDF

	estsDF = pd.read_csv(est)
	with warnings.catch_warnings(): 
	    warnings.simplefilter("ignore") #The warning is not relevent for us
	    estsTemp = StandardScaler().fit_transform(estsDF.values) # Scale stuff so it's normalized and not weird

	# cluster the establishments by price and size of location
	db =DBSCAN(eps = 0.235,min_samples = 10).fit(estsTemp)
	labels = db.labels_
	#Append cluster to establishments
	estsDF['Clusters'] = labels

	usersDF['Gender'] = usersDF['Gender'].astype('category')
	usersDF['employment'] = usersDF['employment'].astype('category')

	#Assign weighted categories to each location. Categories was computed from the cluster centers
	uniqueLocs = set(checksDF.location.values)
	labelSet = set(labels)
	weights = [0.07,0.1,0.2,0.3,0.33]
	locPriceMap = {}
	for eachLoc in uniqueLocs:
	    locPriceMap[eachLoc] = np.random.choice(list(labelSet),p=weights)
	#assign clusters appropriately
	checksDF['cluster'] = checksDF.apply(lambda row: locPriceMap[row['location']],axis=1)

	# Assign a random check in to each user
	CheckinData = checksDF.sample(1745).reset_index(drop=True)
	finalData = pd.concat([usersDF,CheckinData],axis=1)

	# Final Clustering
	with warnings.catch_warnings(): 
	    warnings.simplefilter("ignore") #The warning is not relevent for us
	    finalDataNew = StandardScaler().fit_transform(finalData.values) # Scale stuff so it's normalized and not weird

	db = DBSCAN(eps=1.4,min_samples = 7).fit(finalDataNew)
	clusters = db.labels_

	# Assuming update comes as a "id,message"
	# Ad clusters:
	numAdclusters = len(set(clusters))
	adsPerCluster = 5
	availAds = np.array(list(range(adsPerCluster*numAdclusters)))
	availAds = np.reshape(availAds,(numAdclusters,adsPerCluster))

	def serve_ad(userId,clusters):
	    userClus = clusters[userId]
	    return random.choice(availAds[userClus])

		# The callback for when the client receives a CONNACK response from the server.
	def on_connect(client, userdata, flags, rc):
	    print("Connected with result code "+str(rc))
	    print("Use publish/update as publishing topic")
	    print("Use receive/update as receiving topic")

	    # Subscribing in on_connect() means that if we lose the connection and
	    # reconnect then subscriptions will be renewed.
	    client.subscribe("test/topic")

	# The callback for when a PUBLISH message is received from the server.
	def on_message(client, userdata, msg):
	    data = msg.payload.decode(encoding="utf-8")
	    print(data)
	    parsed = data.strip().split(",",1)  # split on first comma
	    user = int(parsed[0])
	    message = parsed[1]
	    ad = serve_ad(user,clusters)
	    event = '{{user_id : {0} , ad_id : {1}}}'.format(user,ad)# % user, ad
	    client.publish("receive/update",event)#publish
	    
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect("localhost", 1883, 60)

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	client.loop_forever()
    



if __name__ == "__main__": main()