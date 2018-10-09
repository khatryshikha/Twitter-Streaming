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

#Homepage
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
		return render(request,'error_page.html',context)
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
			user_details = {key: data['user'][key] for key in user_keys}
			user_details["name_lower"] = data['user']['name'].lower()
			user_details["screen_name_lower"] = data['user']['screen_name'].lower()
			user_details['favourites_count'] = data['user']['favourites_count']
			if data['user']['location']:
				user_details["location_lower"] = data['user']['location'].lower()
			users.insert(user_details)
		data['user'] = data['user']['id']
		data_keys = ['favorite_count', 'id', 'is_quote_status', 'lang', 'retweet_count','user']
		tweet_detail = {key: data[key] for key in data_keys}

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

# API-2 Filtering and soting data 
def search_data(request):
	name = request.POST.get('name')
	text = request.POST.get('text')
	location = request.POST.get('location')
	language = request.	POST.get('language')
	retweet_count = request.POST.get('rtcount')
	follower = request.POST.get('followers')
	startdate = request.POST.get('startdate')
	enddate = request.POST.get('enddate')
	tweet_favcount = request.POST.get('favcount')
	sortField = request.POST.get('sortField')
   	order = request.POST.get('order')
	# check_export = request. POST.get('checked')

	print retweet_count
	result = []
	users = db.users
	tweets = db.tweets
	if (name != "" ):
		print 'a'
		sd = users.find({'name_lower':{'$regex' : str(name.lower())}})
		for i in sd:
			ed = tweets.find_one({'user':int(i['id'])})
			z = merge_two_dicts(i,ed)
			result.append(z)
	
	if (text != "" ):
		print 'b'
		sd = tweets.find({'text_lower' :{'$regex' : str(text.lower())}})
		for i in sd:
			ed = users.find_one({'id':long(i['user'])})
			z = merge_two_dicts(i,ed)
			result.append(z)
		
	if (location != "" ):
		print 'c'
		sd = users.find({'location_lower':{'$regex' : str(location.lower())}})
		for i in sd:
			ed = tweets.find_one({'user':long(i['id'])})
			z = merge_two_dicts(i,ed)
			result.append(z)
	
	if (language != ""):
		print 'd'
		sd = tweets.find({'lang' :{'$regex' : str(language.lower())}})
		for i in sd:
			ed = users.find_one({'id':long(i['user'])})
			z = merge_two_dicts(i,ed)
			result.append(z)
			

	if (retweet_count != ""):
		print 'e'
		sd = tweets.find({'retweet_count' :{'$regex' : int(retweet_count)}})
		for i in sd:
			ed = users.find_one({'id':long(i['user'])})
			z = merge_two_dicts(i,ed)
			result.append(z)

	if (follower != "" ):
		print 'f'
		sd = users.find({'followers_count':{'$regex' : int(follower)}})
		for i in sd:
			ed = tweets.find_one({'user':long(i['id'])})
			z = merge_two_dicts(i,ed)
			result.append(z)

	if (tweet_favcount != ""):
		print 'g'
		sd = users.find({'favourites_count' :{'$regex' : int(tweet_favcount)}})
		for i in sd:
			ed = tweets.find_one({'user':long(i['id'])})
			z = merge_two_dicts(i,ed)
			result.append(z)
	
    # sorting 
	if (order == 'Ascending'):
		newresults = sorted(result, key=itemgetter(sortField), reverse=True)
	else:
		newresults = sorted(result, key=itemgetter(sortField), reverse=False)
    
	print newresults
	return render(request,'home_page.html')

def merge_two_dicts(x, y):
	z = x.copy()
	z.update(y)
	return z
	
