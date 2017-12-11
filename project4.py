# Emily Behnan Final Project

import FBinfo
import sqlite3
import requests
import datetime
import facebook  #import facebook-sdk
import json
from pprint import pprint
import plotly
import plotly.plotly as py
import plotly.graph_objs as go



## Set up of the caching pattern

CACHE_FNAME = "user_cached_data.json"

try:

    cache_file = open(CACHE_FNAME,'r') #trying to read file
    cache_contents = cache_file.read() #data into string if present
    CACHE_DICTION = json.loads(cache_contents) #putting into a dictionary
    cache_file.close() #close file, we are good & the data is in a dictionary
except:

    CACHE_DICTION = {}


################################## Facebook Graph API ####################################

## Gathering Facebook Data: gets 100 Facebook photo posts from a
## a specific user's feed while using caching. my_facebook_data function
## returns a Python object to represent the data retrieved from Facebook

def user_facebook_data(my_access_token):  #my_access_token linked to FBinfo.py

    graph = facebook.GraphAPI(access_token=my_access_token, version="2.1") #Graph API is made up of objects/nodes in FB (people, pages, events, photos) & connections between them
    user_facebook_data = graph.request('me?fields=photos.limit(100){likes,comments,created_time}')
    #nested request using field expansion to retrieve up to 100 photos on a user's profile
    #with people who liked, comments, and the time created

    user_id = user_facebook_data['id']
    user_photo_list = user_facebook_data['photos']['data'] #retrieves photo data, list of users' Name who liked and users' ID, comments, time created


    user_facebook_results = [] #creates empty list for caching data

    if user_id in CACHE_DICTION: #if we have already made this request, use stored data in cache

        user_facebook_results = CACHE_DICTION[user_id]

    else: #otherwise, get data from Facebook API Graph

        for user_post in user_photo_list:   #iterates through all photo data
            amount_of_likes = 0     #initializes number of likes per photo

            photo_likes=user_post.keys()

            if 'likes' in photo_likes:  #iterates through keys to find "likes"
                for like in user_post['likes']['data']: #retrieves all data of users who liked photo
                    amount_of_likes += 1    #accumulation of number of users who liked each photo

            user_created_time = user_post['created_time']

            user_day = user_created_time[8:10] #retrieves day of picture post
            user_month = user_created_time[5:7] #retrieves month of picture post
            user_year = user_created_time[:4] #retrieves year of picture post

            user_weekday = datetime.datetime(int(user_year), int(user_month), int(user_day))  #uses datetime module to create integer values for year,month, and day
            user_weekday = user_weekday.weekday() #method to return integer to match certain weekday (Sunday-Monday)

            if user_weekday == 0:
                weekday = "Monday"

            elif user_weekday == 1:
                weekday = "Tuesday"

            elif user_weekday == 2:
                weekday = "Wednesday"

            elif user_weekday == 3:
                weekday = "Thursday"

            elif user_weekday == 4:
                weekday = "Friday"

            elif user_weekday == 5:
                weekday = "Saturday"

            elif user_weekday == 6:
                weekday = "Sunday"

            else:
                print("Not a Valid Date")

            user_facebook_results.append((amount_of_likes, weekday))    #creates list of tuples of amount of likes on specific days of the week


        CACHE_DICTION[user_id] = user_facebook_results
        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close()

    return user_facebook_results  #returns list of tuples of # of likes with the day of week of photo post



################################### SQL Database ###############################

conn = sqlite3.connect("user_facebook_database.sqlite")
curs = conn.cursor()

curs.execute("DROP TABLE IF EXISTS Likes_On_Photos_By_Day_Of_The_Week")
curs.execute("CREATE TABLE Likes_On_Photos_By_Day_Of_The_Week (Weekday TEXT, Likes NUMBER)") #creates table

user_data=user_facebook_data(FBinfo.access_token)
for each_photo in user_facebook_data(FBinfo.access_token):

    fb_tuple = (each_photo[1], each_photo[0])  #creates tuples to correspond to each column
    curs.execute('INSERT INTO Likes_On_Photos_By_Day_Of_The_Week (Weekday, Likes) VALUES (?,?)', fb_tuple)  #inserts appropiate values into corresponding column

    conn.commit()

curs.close()

#######################plotly visualization#########################

plotly.tools.set_credentials_file(username='embehnan', api_key='cUwRg6W1b5CeTciGcp1U')
