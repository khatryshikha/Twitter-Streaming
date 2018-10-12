# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from tweepy import OAuthHandler
from tweepy import Stream
import csv
import json
from datetime import datetime
from tweepy.streaming import StreamListener
from django.views.decorators.csrf import csrf_exempt
from .database import dbs as db
import itertools
from operator import itemgetter
# Create your views here.
import time
from django.conf import settings

ACCESS_TOKEN = "802829156698365952-qQNT1TEO71DDxxjBHfP1zPo96DwrZT3"
ACCESS_TOKEN_SECRET = "HNCKoCwkhT40d8KSRaSA2Rx7F90g2vudIlmYrt2tIHOQh"
CONSUMER_KEY = "8Qq2OVMxT8llyzMQCBIZJQk1N"
CONSUMER_SECRET = "RL2En81XXUDF1go4p70IfCFvyxK9qyAPPw4Xt4tOnhkifFJ2nD"

from .api1 import *


def Merge(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

# API-2 Filtering and soting data 
@csrf_exempt
def search_data(request):
	if request.method == 'POST':
		user_name = request.POST.get('user_name')
		tweet_text = request.POST.get('tweet_text')
		location = request.POST.get('location')
		language = request.	POST.get('language')
		retweet_count = request.POST.get('rtcount')
		follower = request.POST.get('followers')
		startdate = request.POST.get('startdate')
		enddate = request.POST.get('enddate')
		tweet_favcount = request.POST.get('favcount')
		sortField = request.POST.get('sfield')
		order = request.POST.get('order')
		page = request.POST.get('page')
	elif request.method == 'GET':
		user_name = request.GET.get('user_name')
		tweet_text = request.GET.get('tweet_text')
		location = request.GET.get('location')
		language = request.	GET.get('language')
		retweet_count = request.GET.get('rtcount')
		follower = request.GET.get('followers')
		startdate = request.GET.get('startdate')
		enddate = request.GET.get('enddate')
		tweet_favcount = request.GET.get('favcount')
		sortField = request.GET.get('sfield')
		order = request.GET.get('order')
		page = request.GET.get('page')
#&order=asc&sfield=favourites_count
	# return JsonResponse({"as":"asd"})
	result = []
	users = db.users
	tweets = db.tweets
	if (user_name != None and tweet_text != None):
		print 'both'
		typefilter = user_name[0] + user_name[1]
		user_name = user_name[3:]
		if typefilter == 'em':
			user_info = users.find_one({"name_lower": str(user_name)})
		elif typefilter =='co':
			user_info = users.find_one({"name_lower":{'$regex':str(user_name)}})
		elif typefilter == 'sw':
			user_info = users.find_one({"name_lower":{'$regex': "^"+str(user_name)}})
		elif typefilter == 'ew':
			user_info = users.find_one({"name_lower":{'$regex': str(user_name)+"$"}})
		
		if user_info == None:
			a = [{}]
			a = json.dumps(a)
			return JsonResponse(a, safe=False)
		all_tweets = tweets.find({'user': int(user_info['id']), 'text_lower': { '$regex': str(tweet_text) } })
		user_info.pop('_id', None)
		for i in all_tweets:
			i.pop('_id', None)
			k = Merge(user_info, i)
			result.append(k)

	elif (user_name != None):
		user_name = user_name.lower()
		typefilter = user_name[0] + user_name[1]
		user_name = user_name[3:]
		if typefilter == 'em':
			user_info = users.find_one({"name_lower": str(user_name)})
		elif typefilter =='co':
			user_info = users.find_one({"name_lower":{'$regex':str(user_name)}})
		elif typefilter == 'sw':
			user_info = users.find_one({"name_lower":{'$regex': "^"+str(user_name)}})
		elif typefilter == 'ew':
			user_info = users.find_one({"name_lower":{'$regex': str(user_name)+"$"}})
		if user_info == None:
			a = [{}]
			a = json.dumps(a)
			return JsonResponse(a, safe=False)
		all_tweets = tweets.find({'user': int(user_info['id'])})
		user_info.pop('_id', None)
		for i in all_tweets:
			i.pop('_id', None)
			k = Merge(user_info, i)
			result.append(k)

	elif (tweet_text != None):
		all_tweets = tweets.find({'text_lower': { '$regex': str(tweet_text) } })
		for i in all_tweets:
			user_info = users.find_one({'id': i['users']})
			user_info.pop('_id', None)
			i.pop('_id', None)
			k = Merge(user_info, i)
			result.append(k)
	else:
		all_tweets = tweets.find({})
		for i in all_tweets:
			user_info = users.find_one({'id': i['user']})
			i.pop('_id', None)
			user_info.pop('_id', None)
			k = Merge(user_info, i)
			result.append(k)

	if (location != None ):
		location = location.lower()
		i = 0
		to_del = []
		for i in range(len(result)):
			if  result[i]['location']:
				res_location = result[i]['location'].lower()
				if not location in res_location:
					to_del.append(i)
			else :
				res_location = result[i]['location']
				to_del.append(i)
			
		k = 0
		for i in to_del:
			print i
			del result[i-k]
			k = k + 1	
			
	if (language != None ):
		language = language.lower()
		i = 0
		to_del = []
		for i in range(len(result)):
			if result[i]['lang'] != language:
				to_del.append(i)
		k = 0
		for i in to_del:
			print i
			del result[i-k]
			k = k + 1

	if (retweet_count != None):
		filter = retweet_count[0] + retweet_count[1]
		if not str(filter).isdigit():
			retweet_count = retweet_count[2:]
		if filter == 'eq':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['retweet_count'] != int(retweet_count):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1
	
		elif filter == 'ge':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['retweet_count'] < int(retweet_count):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

		elif filter == 'le':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['retweet_count'] > int(retweet_count):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1
		

	if (follower != None):
		print 'e'
		filter = follower[0] + follower[1]
		if not str(filter).isdigit():
			follower = follower[2:]
		if filter == 'eq':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['followers_count'] != int(follower):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

		elif filter == 'ge':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['followers_count'] < int(follower):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

		elif filter == 'le':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['followers_count'] > int(follower):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

	if (tweet_favcount != None):
		print 'e'
		filter = tweet_favcount[0] + tweet_favcount[1]
		if filter.isalpa():
			tweet_favcount = tweet_favcount[2:]
		if filter == 'eq':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['favorite_count'] != int(tweet_favcount):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

		elif filter == 'ge':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['favorite_count'] < int(tweet_favcount):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1

		elif filter == 'le':
			i = 0
			to_del = []
			for i in range(len(result)):
				if result[i]['favorite_count'] > int(tweet_favcount):
					to_del.append(i)
			k = 0
			for i in to_del:
				print i
				del result[i-k]
				k = k + 1


	if (startdate != None and enddate != None):
		res2 = []
		startdate = datetime.strptime(startdate, "%Y-%m-%d")
		enddate = datetime.strptime(enddate, "%Y-%m-%d")
		for i in result:
			if ( datetime.strptime(i['created_at'], "%Y-%m-%d %H:%M:%S") >= startdate and datetime.strptime(i['created_at'], "%Y-%m-%d %H:%M:%S") <= enddate ):
				res2.append(i)
		result = res2
	elif (startdate != None):
		res2 = []
		startdate = datetime.strptime(startdate, "%Y-%m-%d")
		for i in result:
			if ( datetime.strptime(i['created_at'], "%Y-%m-%d %H:%M:%S") >= startdate):
				res2.append(i)
		result = res2
	elif (enddate != None):
		res2 = []
		enddate = datetime.strptime(enddate, "%Y-%m-%d")
		for i in result:
			if ( datetime.strptime(i['created_at'], "%Y-%m-%d %H:%M:%S") <= enddate ):
				res2.append(i)
		result = res2

	if (order == 'asc'):
		result = sorted(result, key = lambda i: i[sortField]) 
	elif (order == 'dsc'):
		result = sorted(result, key = lambda i: i[sortField], reverse=False)
    
	settings.RESULT = result
	if page != None:
		result = result[((int(page)-1)*10):((int(page))*10)]
	return JsonResponse(result, safe=False)
	
def merge_two_dicts(x, y):
	z = x.copy()
	z.update(y)
	return z

#API3 - CSV export	
def get_csv_export(request):
	results =  settings.RESULT
	with open('output.csv', 'wb') as csvfile:
		spamwriter = csv.writer(csvfile , lineterminator='\n')
		spamwriter.writerow(['ID', 'USER_NAME', 'TWEET','RETWEET_COUNT','FAVOURITE_COUNT','FOLLOWERS','CREATED_AT','LANGUAGE','LOCATION'])
		for i in results:
			print i
			spamwriter.writerow([long(i['id']),i['name'].encode("utf-8"),i['text'].encode("utf-8"),i['retweet_count'],i['favourites_count'],i['followers_count'],i['created_at'],i['lang'],i['location']])
	return JsonResponse( { "Message":"Successfully exported" })