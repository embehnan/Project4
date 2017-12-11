# Emily Behnan Final Project

import emilyinfo
import sqlite3
import requests
import datetime
import facebook  #import facebook-sdk
import json
from pprint import pprint


## Set up of the caching pattern

CACHE_FNAME = "my_cached_data.json"

try:

    cache_file = open(CACHE_FNAME,'r') #trying to read file
    cache_contents = cache_file.read() #data into string if present
    CACHE_DICTION = json.loads(cache_contents) #putting into a dictionary
    cache_file.close() #close file, we are good & the data is in a dictionary
except:

    CACHE_DICTION = {}


## Facebook Graph API ##

## Gathering Facebook Data: gets 100 Facebook photo posts from a
## a specific user's feed while using caching. my_facebook_data function
## returns a Python object to represent the data retrieved from Facebook

def my_facebook_data(my_access_token):  #my_access_token linked to emilyinfo.py

    graph = facebook.GraphAPI(access_token=my_access_token, version="2.1") #Graph API is made up of objects/nodes in FB (people, pages, events, photos) & connections between them
    my_facebook_data = graph.request('me?fields=photos.limit(100){likes,comments,created_time}')
    #nested request using field expansion to retrieve up to 100 photos on a user's profile
    #with people who liked, comments, and the time created

    my_id = my_facebook_data['id'] #
    my_photo_list = my_facebook_data['photos']['data'] #

    my_facebook_results = []

    if my_id in CACHE_DICTION: #if we have already made this request, use stored data in cache

        my_facebook_results = CACHE_DICTION[my_id]

    else: #otherwise, get data from Facebook API Graph and store it

        for my_post in my_photo_list:
            amount_of_likes = 0

            if 'likes' in my_post.keys():
                for like in my_post['likes']['data']:
                    amount_of_likes += 1

            my_created_time = my_post['created_time']
            my_year = my_created_time[:4]
            my_month = my_created_time[5:7]
            my_day = my_created_time[8:10]

            my_weekday = datetime.datetime(int(my_year), int(my_month), int(my_day))
            my_weekday = my_weekday.weekday()

            if my_weekday == 0:
                weekday = "Monday"

            elif my_weekday == 1:
                weekday = "Tuesday"

            elif my_weekday == 2:
                weekday = "Wednesday"

            elif my_weekday == 3:
                weekday = "Thursday"

            elif my_weekday == 4:
                weekday = "Friday"

            elif my_weekday == 5:
                weekday = "Saturday"

            elif my_weekday == 6:
                weekday = "Sunday"

            else:
                print("Not a Valid Date")

            my_facebook_results.append((amount_of_likes, weekday))

        CACHE_DICTION[my_id] = my_facebook_results
        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close()

    return my_facebook_results


## SQL Database

conn = sqlite3.connect("my_facebook_database.sqlite")
curs = conn.cursor()

curs.execute("DROP TABLE IF EXISTS Likes_On_Photos_By_Day_Of_The_Week")
curs.execute("CREATE TABLE Likes_On_Photos_By_Day_Of_The_Week (Weekday TEXT, Likes NUMBER)")

my_data=my_facebook_data(emilyinfo.access_token)
for each_photo in my_data:

    fb_tuple = (each_photo[1], each_photo[0])
    curs.execute('INSERT INTO Likes_On_Photos_By_Day_Of_The_Week (Weekday, Likes) VALUES (?,?)', fb_tuple)

    conn.commit()

curs.close()
