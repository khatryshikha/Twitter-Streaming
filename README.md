# Twitter Streaming API
GitHub Repository Link : https://github.com/khatryshikha/Twitter-Streaming



This set of APIs has been created to store twitter streaming data and retrieve data based on applied filters. It is a set of 3 APIs-
1. [API for Twitter Stream](#1-api-to-trigger-twitter-stream-stream)
2. [API to filter/search stored tweets](#2-api-to-filtersearch-stored-tweets-search)
3. [API to export filtered data to CSV](#3-api-to-export-filtered-data-in-csv-getcsv)

Technologies used:
  - Python/ Django framework
  - MongoDB
  - Twitter Streaming API
  <!-- - MongoDB (Hosted on MLab) -->
  
## Move To
- [Installation Instructions](#installation-instructions)
- [API 1 - API for Twitter Stream](#1-api-to-trigger-twitter-stream-stream)
- [API 2 - API to filter/search stored tweets](#2-api-to-filtersearch-stored-tweets-search)
- [API 3 - API to export filtered data to CSV](#3-api-to-export-filtered-data-in-csv-getcsv)
  
## Installation Instructions
  1. clone the project
  `git clone https://github.com/khatryshikha/Twitter-Streaming.git`
  2. cd to project folder `cd Twitter-Streaming` and create virtual environment
  `virtualenv venv`
  3. activate virtual environment
  `source venv/bin/activate`
  4. install requirements
  `pip install -r requirements.txt`
  5. run the server
  `python manage.py runserver`
   
## 1. API for Twitter Stream (/twitter/stream)
This API triggers twitter streaming and stores a curated version of the data returned by Twitter Streaming API. The streaming is done as per the given parameters.

API - `http://127.0.0.1:8000/twitter/stream?<keyword><count><time>`
(methods supported - GET, POST)

- Where `<keyword>` can be any keyword for which streaming needs to be performed.
- Where `<count>` the streaming runs till given number of tweets are received .
- Where `<time>` the streaming runs for given time (seconds) .
    
  <b>Examples:</b>
  ```
  http://127.0.0.1:8000/twitter/stream?keyword=modi&count=10 (runs till 10 tweets are fetched for keyword 'modi')
  http://127.0.0.1:8000/twitter/stream?keyword=modi&time=10 (runs for 10 seconds to fetch tweets for keyword 'modi')
  http://127.0.0.1:8000/twitter/stream?keyword=modi&count=10&time=10 (stops streaming whichever comes first i.e. 10 tweets or 10 seconds)
  ```
  ### API Response
  | Parameter | Meaning |
  | ------ | ------ |
  | code | 0 (successful)/ 1(failed) |
  | status | success/failed |


  
  <b>Examples:</b>
  
  1. Successful response
   ```
  {
    "status": "success",
    "Message": "Succesfully added twitter data to database",
    "code": "0"
  }
  ```

  2. Failed Response
   ```
  a) When `<time>` or `<count>` parameters are not passed.


  {
    "status": "failed",
    "Message": "No Parameters Passed",
    "code": "1"
  }



  b) When failed to fetch data.


  {
    "status": "failed",
    "Message": "Some error occured",
    "code": "1"
    }
    
  ```


## 2. API to filter/search stored tweets (/twitter/search)
This API fitler or search the fetched data stored by the [first api](#1-api-to-trigger-twitter-stream) and sorts them as required.

API - `http://127.0.0.1:8000/twitter/filter?<filter>[parameters]<sortfield><order><page>`
(methods supported - GET, POST)

<b>Following are the elements of the api:</b>
### Filters ([filter])
Initially this API is used to filter the data by tweet text/user name i.e `<filter>=<user_name>` or `<filter>=<tweet_text>` where these `<filter>` can be futher filtered by one or more parameters or if `<filter>=<none>` then this API use all data to filter data as mentioned below and `<value>` should be in the specified format.
  
  
Following parameters can be applied:

  | Filter | Meaning | Value Format (refer table below) | Example |
  | ------ | ----- | ------ | ----- |
  | user_name | filter tweets by screen_name (case insensitive) | `<textFilterType>-<filterValue>` | user_name=co-shikha | 
  | tweet_text | filter tweets from tweet content (case insensitive) | `<filterValue>` | tweet_text=Silver |
  | location | location of the user posting the tweet (case insensitive) | `<location>` | location=Jaipur |
  | language | Language of tweet | any specific language in [BCP 47](https://tools.ietf.org/html/bcp47) format | language=en |
  | retweet_count (mostly 0) | retweet count of tweet | `<numFilterType><filterValue>`| rtcount=eq100 |
  | follower | number of followers of the user | `<numFilterType><filterValue>`| followers=le100 |
  | tweet_favorite_count (mostly 0) | favourite count of tweet | `<numFilterType><filterValue>`| favcount=ge10 |
  | startdate | Tweets posted on or after a specific date | `yyyy-mm-dd` | startdate=2018-10-12 |
  | enddate | Tweets posted on or before a specific date | `yyyy-mm-dd` | enddate=2018-10-14 |
  
  In the format `<textFilterType>-<filterValue>`,`<textFilterType>` can be

  | textFilterType | Meaning |
  | ------ | ------ |
  | sw | starts with |
  | ew | ends with |
  | co | contains |
  | em | exact match |
  
  In the format `<numFilterType><filterValue>`, `<numFilterType>` can be

  | numFilterType | Meaning |
  | ------ | ------ |
  | eq | equal to |
  | ge | greater than or equal to |
  | le | less than or equal to |
  
### Sort ([sort])
Sorting can be done by any filter, parameter , date of tweet in both ascending and descending order. By default, sorting is done by name of user in ascending order The format of `<order>` & `<sfield(sortField)>`

where  `<order>` can be

  | order | Meaning |
  | ------ | ----- |
  | asc | Ascending order |
  | dsc | descending order |
  
and `<sfield>` can be any field .

  | sortField | Meaning | Example |
  | ------ | ------ | ------ |
  | name | sort by name | sfield=name |
  | screen_name | sort by screen name | sfield=screen_name |
  | retweet_count | sort by retweet count | sfield=retweet_count |
  | followers_count | sort by follower count of user | sfield=followers_count |
  | created_at | sort by date | sfield=created_at |
  | tweet_text | sort by tweet text | sfield=text |
  | tweet_favorite_count | sort by favourites count | sfield=favorite_count |
  
### Page ([page])
The API is paginated and returns 10 results in one call. The page number can be specified in the API call as `page=[pageNo]` for example `page=5`. Not speciftying the page number takes to page 1.

<b>Examples</b>
```
http://127.0.0.1:8000/twitter/filter?name=sw-shikha&created_at=2018-10-12&followers_count=gt100&sfield=created_at&order=asc&page=2

```

  
<b>Examples</b>
1. For given API- http://127.0.0.1:8000/twitter/filter/?sfield=name&order=asc&created_at=2018-10-12&page=1 results are as followers :

```
[
  {
        "text_lower": "rt @rishibagree: madhu koda is serving jail sentence for coal scam.\nhis wife geeta koda joins congress in front of rahul gandhi who is out…",
        "is_quote_status": true,
        "text": "RT @rishibagree: Madhu koda is serving Jail sentence for Coal scam.\nHis Wife Geeta Koda joins Congress in front of Rahul Gandhi who is out…",
        "screen_name_lower": "ankit_das1987",
        "user_mentions": "rishibagree",
        "location_lower": "india",
        "user": 802403623552417792,
        "id": 1050643693491769356,
        "favorite_count": 0,
        "screen_name": "ankit_das1987",
        "lang": "en",
        "favourites_count": 19795,
        "name": "ANKIT DAS",
        "keyword": "modi",
        "name_lower": "ankit das",
        "created_at": "2018-10-12 07:05:51",
        "user_mentions_lower": "rishibagree",
        "followers_count": 166,
        "location": "India",
        "retweet_count": 0,
        "is_retweet": true
    },
    {
        "text_lower": "rt @captmrinalc: @manishanataraj @mohua_india @cnbctv18news @pmoindia @myogiadityanath if figures r to b believed, n don’t see no  reason wh…",
        "is_quote_status": false,
        "text": "RT @CaptMrinalC: @manishanataraj @MoHUA_India @CNBCTV18News @PMOIndia @myogiadityanath If figures r to b believed, n don’t see  no reason wh…",
        "screen_name_lower": "captmrinalc",
        "user_mentions": "myogiadityanath",
        "location_lower": "new delhi",
        "user": 1044286855,
        "id": 1050697551488458752,
        "favorite_count": 0,
        "screen_name": "CaptMrinalC",
        "lang": "en",
        "favourites_count": 380,
        "name": "Capt Mrinal",
        "keyword": "modi",
        "name_lower": "capt mrinal",
        "created_at": "2018-10-12 10:39:51",
        "user_mentions_lower": "myogiadityanath",
        "followers_count": 390,
        "location": "New Delhi",
        "retweet_count": 0,
        "is_retweet": true
    }
    ....
  ]

```

## 3. API to export filtered data to CSV (/twitter/export)
This API exports the data to CSV file. It contains the specific field that are filtered and sorted in the [Second API](#2-api-to-filtersearch-stored-tweets-search), if no filter applied then all the data will be exported to the CSV file. There is no `[page]` parameter as all the matching data is returned.


API : `http://127.0.0.1:8000/twitter/export`
(methods supported - GET, POST)

### API Response
If the request to the API is sent, it downloads a CSV file containing data based on filters.
