# Emily Behnan Final Project

import sqlite3
import requests
import datetime
import facebook  #pip install facebook-sdk
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

access_token = None
if access_token is None:
    access_token = input("\nCopy and paste token from https://developers.facebook.com/tools/explorer\n>  ") #how to get Facebook access token

def user_facebook_data(access_token):

    graph = facebook.GraphAPI(access_token, version="2.1") #Graph API is made up of objects/nodes in FB (people, pages, events, photos) & connections between them
    user_facebook_data = graph.request('me?fields=photos.limit(100){likes,comments,created_time}')
    #nested request using field expansion to retrieve up to 100 photos on a user's profile
    #with people who liked, comments, and the time created

    user_id = user_facebook_data['id']
    user_photo_list = user_facebook_data['photos']['data'] #retrieves photo data, list of users' Name who liked and users' ID, comments, time created

    user_facebook_results = [] #creates empty list for caching data


    if user_id in CACHE_DICTION: #if we have already made this request, use stored data in cache

        user_facebook_results = CACHE_DICTION[user_id]

    else:
        while True:
            try:
                with open('my_posts.json','a') as f: #saves raw API response as cache file in my_posts.json
                    for post in user_facebook_data['photos']['data']:
                        f.write(json.dumps(post)+"\n")
                    user_facebook_data = requests.get(user_facebook_data['paging']['next']).json()
            except KeyError:
        		#ran out of posts
                break

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

            user_facebook_results.append((amount_of_likes, weekday))


        CACHE_DICTION[user_id] = user_facebook_results #puts a dictionary named as the users fb id,
        #and inside dictionary is a list of lists of amount of likes on specific days of the week

        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close() #closing file

    return user_facebook_results  #returns # of likes with the day of week of photo post



################################### SQL Database ###############################

conn = sqlite3.connect("user_facebook_database.sqlite")
curs = conn.cursor()

curs.execute("DROP TABLE IF EXISTS Likes_On_Photos_By_Day_Of_The_Week")
curs.execute("CREATE TABLE Likes_On_Photos_By_Day_Of_The_Week (Weekday TEXT, Likes NUMBER)") #creates table

user_data=user_facebook_data(access_token)
for each_photo in user_facebook_data(access_token):

    fb_tuple = (each_photo[1], each_photo[0])  #creates tuples to correspond to each column
    curs.execute('INSERT INTO Likes_On_Photos_By_Day_Of_The_Week (Weekday, Likes) VALUES (?,?)', fb_tuple)  #inserts appropiate values into corresponding column

    conn.commit()

curs.close()

#######################Counting Days of the Week############
count_dict = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}
#initializes a dictionary to tally the number of photos posted each day of the week

with open("user_cached_data.json", 'r') as infile:  #loading json file to read as infile
    read = infile.read()
    data = json.loads(read)
    count_list = data["1133532416662509"] #retrieving the dictionary with the key value as the user's id

    for lst in count_list:   #iterating through the lists inside dictionary
        day = lst[1]  #indexing the second item (day of week) in each list
        count_dict[day] += 1  #summing every occurance of each day of the week and adding them as values to the counter dictionary

    keys_lst = list(count_dict.keys())  #creating list for all keys in count_dict (Monday-Sunday)
    vals_lst = list(count_dict.values()) #creating list for all values in count_dict (# of occurance of each day of week)


#######################plotly visualization#########################

plotly.tools.set_credentials_file(username='embehnan', api_key='cUwRg6W1b5CeTciGcp1U')  #accessing my plotly account

#code pattern for bar chart retrieved from https://plot.ly/python/bar-charts/

 #creating bar chart with x values as day of week, and y values as # of photos posted on each day of week

chart = go.Bar(
            x=keys_lst,
            y=vals_lst,
            text=vals_lst,
            textposition = 'auto',
            marker=dict(
                color='rgb(158,202,225)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            ),
            opacity=0.6
        )

data = [chart]
layout = go.Layout(title='Number of Facebook Photos Posted by Day of the Week',)

fig = go.Figure(data=data, layout=layout)

py.plot(fig, filename='bar-direct-labels') #this allows for the visualization to automatically pop up in a browser
