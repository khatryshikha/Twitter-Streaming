# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import csv
import time
import datetime
from .database import dbs as db
import itertools
from operator import itemgetter
# Create your views here.

def Homepage(request):
    return render(request,'home_page.html')

def twitter_streaming(request):
    return render(request,'search.html')


def searchdate(request):
    if request.method == 'POST' :
        filterValue1 = request.POST.get('filterValue1')
        filterValue2 = request.POST.get('filterValue2')
        filterValue3 = request.POST.get('filterValue3')
        textFilterType = request.POST.get('textFilterType')
        numFilterType = request.POST.get('numFilterType')
        sortField = request.POST.get('sortField')
        order = request.POST.get('order')
        check_export = request. POST.get('checked')
        text_field1 = request.POST.get('Search')
        text_field2 = request.POST.get('Search1')
        text_field3 = request.POST.get('Search2')
        
    results = []
    tweetdb = db.tweeet
    if (text_field1 != "" and (filterValue1 == 'name' or filterValue1 == 'ttxt' or filterValue1 == 'user_mentions' or filterValue1 == 'sname')):
        print 'enter1'
        results = filter_by_text(filterValue1,text_field1,textFilterType)
    
    if ((filterValue2 == 'favcount' or filterValue2 == 'rtcount' or filterValue2 == 'start_date' or filterValue2 == 'end_date' or filterValue1 == 'followers') and text_field2 != ""):
        results = filter_range(text_field2,numFilterType)

    # if (filterValue2 == 'start_date' or filterValue2 == 'end_date'):
    #     if (text_field2 != None and len(text_field2)==10):
    #         text_field2 = text_field2.translate(None,'-')
    #         date_time = str(datetime.datetime.strptime(text_field2 , '%Y%m%d'))
    #         # if only or date+time
    #         date = date_time.split(' ')
    #         if(numFilterType == 'gt'):
    #             results = tweetdb.find({'created_at':{'$gt': date[0]}})
    #         elif (numFilterType == 'lt'):
    #             results = tweetdb.find({'created_at': {'$lt' : date[0]}})
    #         elif(numFilterType == 'none' or numFilterType == 'eq'):
    #             results = tweetdb.find({'created_at': date[0]})

    #         elif (numFilterType == 'gte'):
    #             results = tweetdb.find({'created_at':{'$gte': date[0]}})
    #         else:
    #             results = tweetdb.find({'created_at': {'$lte' : date[0]}})
       
    if(filterValue3 == 'location' and text_field3 != ""):
        results = list(tweetdb.find({'location': str(text_field3) }))

    if(filterValue3 == 'language' and text_field3 != ""):
        results = tweetdb.find({'language': text_field3.lower() })	
				

    sorting 
    if (order == 'Ascending'):
        newresults = sorted(results, key=itemgetter(sortField), reverse=False)
    else:
        newresults = sorted(results, key=itemgetter(sortField), reverse=True)
    print results

    if(check_export == 'on'):
        with open('output.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile , lineterminator='\n')
            spamwriter.writerow(['uid', 'user', 'tweet','retweet_count','fav_count','followers','created_at','language','location'])
            for i in results:  
                print i
                for k in i:
                    print k
                spamwriter.writerow([int(i['uid']),int(i['user']),int(i['ttxt']),int(i['rtcount']),int(i['favcount']),int(i['followers']),int(i['created_at']),int(i['language']),int(i['location'])])

    # context ={
        # 'results': newresults, 
        # 'results_count': count, 
		# 'page': page, 										
        # 'next_page':next_page, shikha
		# 'last_page':last_page
    # }
                 
    
    return render(request,'result.html')



def filter_by_text(filterValue1,text_field1,textFilterType):
    tweetdb = db.tweet
    results = []
    ids= list(db.tweet.find({'name' : 'shikha'}))
    print ids
    if (filterValue1 == 'name'):
        if(textFilterType == 'em'):
            print 'entera'
            results = list(tweetdb.find({'name' : text_field1}))
        elif (textFilterType == 'sw'):
            print 'enterb'
            results = list(tweetdb.find({'name' : {'$regex' : "^"+ text_field1 }}))
        elif(textFilterType == 'ew'): 
            print 'enterc'
            results = list(tweetdb.find({'name' : {'$regex' : text_field1 +"$"}}))
        else : 
            print 'enterd'
            results = list(tweetdb.find_one({'name' : {'$regex' : text_field1 }}))
        
    if (filterValue1 == 'ttxt'):
        if(textFilterType == 'em'):
            results = list(tweetdb.find({'ttxt' : text_field1}))
        elif(textFilterType == 'sw'):
            results = list(tweetdb.find({'ttxt' : {'$regex' : "^"+ text_field1 }}))
        elif (textFilterType == 'ew'): 
            results = list(tweetdb.find({'ttxt' : {'$regex' : text_field1 +"$"}}))
        else : 
            results = list(tweetdb.find({'ttxt' : {'$regex' : text_field1 }}))

    if (filterValue1 == 'user_mentions'):
        if(textFilterType == 'em'):
            results = list(tweetdb.find({'user_mentions' : text_field1}))
        elif (textFilterType == 'sw'):
            results = list(tweetdb.find({'user_mentions' : {'$regex' : "^"+ text_field1 }}))
        elif (textFilterType == 'ew'): 
            results = list(tweetdb.find({'user_mentions' : {'$regex': text_field1 +"$"}}))
        else : 
            results = list(tweetdb.find({'user_mentions' : {'$regex' : text_field1 }}))
    print results
    return results

def filter_range(text_field2,numFilterType):
    tweetdb = db.tweet
    results = []
    if(text_field2 != None):
        if (numFilterType == 'gt'):
            if (favcount != None):
                results = tweetdb.find({'favcount': {'$gt':int(text_field2)}})
            if(rtcount != None):
                results = tweetdb.find({'rtcount': {'$gt':int(text_field2)}})
            if(followers != None):
                results = tweetdb.find({'followers': {'$gt':int(text_field2)}})
        elif (numFilterType == 'lt'):
            if (favcount != None):
                results = tweetdb.find({'favcount': {'$lt':int(text_field2)}})
            if(rtcount != None):
                results = tweetdb.find({'rtcount': {'$lt':int(text_field2)}})
            if(followers != None):
                results = tweetdb.find({'followers': {'$lt':int(text_field2)}})
        elif (numFilterType == 'eq' or numFilterType == 'none'):
            if (favcount != None):
                results = tweetdb.find({'favcount': int(text_field2)})
            if(rtcount != None):
                results = tweetdb.find({'rtcount': int(text_field2)})
            if(followers != None):
                results = tweetdb.find({'followers': int(text_field2)})
        elif (numFilterType == 'ge'):
            if (favcount != None):
                results = tweetdb.find({'favcount': {'$gte':int(text_field2)}})
            if(rtcount != None):
                results = tweetdb.find({'rtcount': {'$gte':int(text_field2)}})
            if(followers != None):
                results = tweetdb.find({'followers': {'$gte':int(text_field2)}})
        elif (numFilterType == 'le'):
            if (favcount != None):
                results = tweetdb.find({'favcount': {'$lte':int(text_field2)}})
            if(rtcount != None):
                results = tweetdb.find({'rtcount': {'$lte':int(text_field2)}})
            if(followers != None):
                results = tweetdb.find({'followers': {'$lte':int(text_field2)}})
        if (results == None):
            error_page()
    return results

