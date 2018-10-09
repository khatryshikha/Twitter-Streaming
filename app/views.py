# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from tweepy import OAuthHandler
from tweepy import Stream
import csv
import json
from datetime import datetime
from tweepy.streaming import StreamListener
from .database import dbs as db
import itertools
from operator import itemgetter
# Create your views here.

ACCESS_TOKEN = "802829156698365952-qQNT1TEO71DDxxjBHfP1zPo96DwrZT3"
ACCESS_TOKEN_SECRET = "HNCKoCwkhT40d8KSRaSA2Rx7F90g2vudIlmYrt2tIHOQh"
CONSUMER_KEY = "8Qq2OVMxT8llyzMQCBIZJQk1N"
CONSUMER_SECRET = "RL2En81XXUDF1go4p70IfCFvyxK9qyAPPw4Xt4tOnhkifFJ2nD"

def Homepage(request):
    return render(request,'home_page.html')

#API 1 - To stream data based on keyword/time/count
def twitter_streaming(request):
	keyword = request.POST.get('keyword')
	keyword = str(keyword)
	time = request.POST.get('time')
	count = request.POST.get('count')
	try:
		if time == None or time == "":
			time = 0
		if count == None or count == "":
			count = 0
		if time == 0 and count ==0:
			context = {
						"code":"1","status":"failed",
						"message":"No Parameters Passed"
					}
			return render(request,'error_page.html',context)
		l = StdOutListener(int(time), int(count), keyword)

		auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
		auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		stream = Stream(auth, l)
		stream.filter(track=[keyword])
	except:
		context = {
					"code":"1","status":"failed",
					"message":"Some error occured"
				}
		return render(request,'error.html',context)
	return render(request,'search.html')
	

# StreamListener class for working on streaming tweets
class StdOutListener(StreamListener):
	def __init__(self, time, count, keyword):
		self.maxtweet = count
		self.time = time
		self.tweetcount = 0
		self.starttime = datetime.now()
		self.keyword = keyword

	def on_data(self, data):
		if self.time and (datetime.now()-self.starttime).seconds >= self.time:
			return False

		data_load= json.loads(data)
		storeData(data_load, self.keyword)

		self.tweetcount+=1
		if self.time and (datetime.now()-self.starttime).seconds >= self.time:
			return False

		if self.maxtweet and self.tweetcount >= self.maxtweet:
			return False

		return True

	def on_error(self, status):
		print status

#Function to store curated data in database
def storeData(data, keyword):
	users = db.users
	tweets = db.tweets
	tweet_test = tweets.find_one({'id':data['id']})
	if tweet_test == None:
		user_keys = ['id','screen_name', 'name', 'location', 'followers_count']
		user_test = users.find_one({'id':data['user']['id']})
		if user_test == None:
			for key in user_keys:
				user_details = {key: data['user'][key] }
			user_details["name_lower"] = data['user']['name'].lower()
			user_details["screen_name_lower"] = data['user']['screen_name'].lower()
			if data['user']['location']:
				user_details["location_lower"] = data['user']['location'].lower()
			users.insert(user_details)

		data['user'] = data['user']['id']
		data_keys = ['favorite_count', 'id', 'is_quote_status', 'lang', 'retweet_count','user']
		for key in data_keys:
			tweet_detail = {key: data[key] }

		if data['truncated'] and 'extended_tweet' in data and 'full_text' in data['extended_tweet']:
			tweet_detail['text'] = data['extended_tweet']['full_text']
		else:
			tweet_detail['text'] = data['text']

		tweet_detail['created_at'] = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
		tweet_detail['text_lower'] = tweet_detail['text'].lower()
		for x in data['entities']['hashtags']:
			tweet_detail['hashtags'] = x['text']
			tweet_detail['hashtags_lower'] = x['text'].lower()
		for x in data['entities']['user_mentions']:
			tweet_detail['user_mentions'] = x['screen_name']
			tweet_detail['user_mentions_lower'] = x['screen_name'].lower()
		tweet_detail['keyword'] = keyword.lower()

		tweet_detail['is_retweet'] = False
		if 'retweeted_status' in data:
			tweet_detail['is_retweet'] = True

		tweets.insert(tweet_detail)
	


#Function to store curated data in database
# def storeData(data, keyword):
# 	users = db.users
# 	tweets =db.tweets
# 	tid_details = tweets.find_one({'id':data['id']})
# 	if tid_details == None:
# 		user_keys = ['id','screen_name', 'name', 'location', 'followers_count']
# 		qtest = users.find_one({'id':data['user']['id']})
# 		if qtest == None:
# 			saveuser = {key: data['user'][key] for key in user_keys}
# 			saveuser["name_lower"] = data['user']['name'].lower()
# 			saveuser["screen_name_lower"] = saveuser["screen_name"].lower()
# 			if data['user']['location']:
# 				saveuser["location_lower"] = data['user']['location'].lower()
# 			users.insert(saveuser)
#             data['user'] = data['user']['id']

# 		data_keys = ['favorite_count', 'id', 'is_quote_status', 'lang', 'retweet_count','user']
# 		savedata = {key: data[key] for key in data_keys}

# 		if data['truncated'] and 'extended_tweet' in data and 'full_text' in data['extended_tweet']:
# 			savedata['text'] = data['extended_tweet']['full_text']
# 		else:
# 			savedata['text'] = data['text']

# 		savedata['created_at'] = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
# 		savedata['text_lower'] = savedata['text'].lower()
# 		savedata['hashtags'] = [x['text'] for x in data['entities']['hashtags']]
# 		savedata['hashtags_lower'] = [x['text'].lower() for x in data['entities']['hashtags']]
# 		savedata['user_mentions'] = [x['screen_name'] for x in data['entities']['user_mentions']]
# 		savedata['user_mentions_lower'] = [x['screen_name'].lower() for x in data['entities']['user_mentions']]
# 		savedata['keyword'] = keyword.lower()

# 		savedata['is_retweet'] = False
# 		if 'retweeted_status' in data:
# 			savedata['is_retweet'] = True

# 		tweets.insert(savedata)





# def searchdate(request):
#     if request.method == 'POST' :
#         filterValue1 = request.POST.get('filterValue1')
#         filterValue2 = request.POST.get('filterValue2')
#         filterValue3 = request.POST.get('filterValue3')
#         textFilterType = request.POST.get('textFilterType')
#         numFilterType = request.POST.get('numFilterType')
#         sortField = request.POST.get('sortField')
#         order = request.POST.get('order')
#         check_export = request. POST.get('checked')
#         text_field1 = request.POST.get('Search')
#         text_field2 = request.POST.get('Search1')
#         text_field3 = request.POST.get('Search2')
        
#     results = []
#     tweetdb = db.tweeet
#     if (text_field1 != "" and (filterValue1 == 'name' or filterValue1 == 'ttxt' or filterValue1 == 'user_mentions' or filterValue1 == 'sname')):
#         print 'enter1'
#         results = filter_by_text(filterValue1,text_field1,textFilterType)
    
#     if ((filterValue2 == 'favcount' or filterValue2 == 'rtcount' or filterValue2 == 'start_date' or filterValue2 == 'end_date' or filterValue1 == 'followers') and text_field2 != ""):
#         results = filter_range(text_field2,numFilterType)

#     # if (filterValue2 == 'start_date' or filterValue2 == 'end_date'):
#     #     if (text_field2 != None and len(text_field2)==10):
#     #         text_field2 = text_field2.translate(None,'-')
#     #         date_time = str(datetime.datetime.strptime(text_field2 , '%Y%m%d'))
#     #         # if only or date+time
#     #         date = date_time.split(' ')
#     #         if(numFilterType == 'gt'):
#     #             results = tweetdb.find({'created_at':{'$gt': date[0]}})
#     #         elif (numFilterType == 'lt'):
#     #             results = tweetdb.find({'created_at': {'$lt' : date[0]}})
#     #         elif(numFilterType == 'none' or numFilterType == 'eq'):
#     #             results = tweetdb.find({'created_at': date[0]})

#     #         elif (numFilterType == 'gte'):
#     #             results = tweetdb.find({'created_at':{'$gte': date[0]}})
#     #         else:
#     #             results = tweetdb.find({'created_at': {'$lte' : date[0]}})
       
#     if(filterValue3 == 'location' and text_field3 != ""):
#         results = list(tweetdb.find({'location': str(text_field3) }))

#     if(filterValue3 == 'language' and text_field3 != ""):
#         results = tweetdb.find({'language': text_field3.lower() })	
				

#     sorting 
#     if (order == 'Ascending'):
#         newresults = sorted(results, key=itemgetter(sortField), reverse=False)
#     else:
#         newresults = sorted(results, key=itemgetter(sortField), reverse=True)
#     print results

#     if(check_export == 'on'):
#         with open('output.csv', 'wb') as csvfile:
#             spamwriter = csv.writer(csvfile , lineterminator='\n')
#             spamwriter.writerow(['uid', 'user', 'tweet','retweet_count','fav_count','followers','created_at','language','location'])
#             for i in results:  
#                 spamwriter.writerow([int(i['uid']),int(i['user']),int(i['ttxt']),int(i['rtcount']),int(i['favcount']),int(i['followers']),int(i['created_at']),int(i['language']),int(i['location'])])

#     # context ={
#         # 'results': newresults, 
#         # 'results_count': count, 
# 		# 'page': page, 										
#         # 'next_page':next_page, shikha
# 		# 'last_page':last_page
#     # }
                 
    
#     return render(request,'result.html')



# def filter_by_text(filterValue1,text_field1,textFilterType):
#     tweetdb = db.tweet
#     results = []
#     ids= list(db.tweet.find({'name' : 'shikha'}))
#     print ids
#     if (filterValue1 == 'name'):
#         if(textFilterType == 'em'):
#             print 'entera'
#             results = list(tweetdb.find({'name' : text_field1}))
#         elif (textFilterType == 'sw'):
#             print 'enterb'
#             results = list(tweetdb.find({'name' : {'$regex' : "^"+ text_field1 }}))
#         elif(textFilterType == 'ew'): 
#             print 'enterc'
#             results = list(tweetdb.find({'name' : {'$regex' : text_field1 +"$"}}))
#         else : 
#             print 'enterd'
#             results = list(tweetdb.find_one({'name' : {'$regex' : text_field1 }}))
        
#     if (filterValue1 == 'ttxt'):
#         if(textFilterType == 'em'):
#             results = list(tweetdb.find({'ttxt' : text_field1}))
#         elif(textFilterType == 'sw'):
#             results = list(tweetdb.find({'ttxt' : {'$regex' : "^"+ text_field1 }}))
#         elif (textFilterType == 'ew'): 
#             results = list(tweetdb.find({'ttxt' : {'$regex' : text_field1 +"$"}}))
#         else : 
#             results = list(tweetdb.find({'ttxt' : {'$regex' : text_field1 }}))

#     if (filterValue1 == 'user_mentions'):
#         if(textFilterType == 'em'):
#             results = list(tweetdb.find({'user_mentions' : text_field1}))
#         elif (textFilterType == 'sw'):
#             results = list(tweetdb.find({'user_mentions' : {'$regex' : "^"+ text_field1 }}))
#         elif (textFilterType == 'ew'): 
#             results = list(tweetdb.find({'user_mentions' : {'$regex': text_field1 +"$"}}))
#         else : 
#             results = list(tweetdb.find({'user_mentions' : {'$regex' : text_field1 }}))
#     print results
#     return results

# def filter_range(text_field2,numFilterType):
#     tweetdb = db.tweet
#     results = []
#     if(text_field2 != None):
#         if (numFilterType == 'gt'):
#             if (favcount != None):
#                 results = tweetdb.find({'favcount': {'$gt':int(text_field2)}})
#             if(rtcount != None):
#                 results = tweetdb.find({'rtcount': {'$gt':int(text_field2)}})
#             if(followers != None):
#                 results = tweetdb.find({'followers': {'$gt':int(text_field2)}})
#         elif (numFilterType == 'lt'):
#             if (favcount != None):
#                 results = tweetdb.find({'favcount': {'$lt':int(text_field2)}})
#             if(rtcount != None):
#                 results = tweetdb.find({'rtcount': {'$lt':int(text_field2)}})
#             if(followers != None):
#                 results = tweetdb.find({'followers': {'$lt':int(text_field2)}})
#         elif (numFilterType == 'eq' or numFilterType == 'none'):
#             if (favcount != None):
#                 results = tweetdb.find({'favcount': int(text_field2)})
#             if(rtcount != None):
#                 results = tweetdb.find({'rtcount': int(text_field2)})
#             if(followers != None):
#                 results = tweetdb.find({'followers': int(text_field2)})
#         elif (numFilterType == 'ge'):
#             if (favcount != None):
#                 results = tweetdb.find({'favcount': {'$gte':int(text_field2)}})
#             if(rtcount != None):
#                 results = tweetdb.find({'rtcount': {'$gte':int(text_field2)}})
#             if(followers != None):
#                 results = tweetdb.find({'followers': {'$gte':int(text_field2)}})
#         elif (numFilterType == 'le'):
#             if (favcount != None):
#                 results = tweetdb.find({'favcount': {'$lte':int(text_field2)}})
#             if(rtcount != None):
#                 results = tweetdb.find({'rtcount': {'$lte':int(text_field2)}})
#             if(followers != None):
#                 results = tweetdb.find({'followers': {'$lte':int(text_field2)}})
#         if (results == None):
#             error_page()
#     return results

