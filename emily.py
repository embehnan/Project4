# Emily Behnan Final Project
import emilyinfo
import sqlite3
import requests
import datetime
import facebook
import json
from pprint import pprint

CACHE_FNAME = "my_cached_data.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

# Facebook Graph API
def my_facebook_data(my_access_token):
    graph = facebook.GraphAPI(access_token=my_access_token, version="2.1")
    my_facebook_data = graph.request('me?fields=feed.limit(100){likes,comments,created_time}')
    my_id = my_facebook_data['id']
    my_list_of_posts = my_facebook_data['feed']['data']
    my_facebook_results = []
    if my_id in CACHE_DICTION:
        my_facebook_results = CACHE_DICTION[my_id]
    else:
        for my_post in my_list_of_posts:
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
                print("Invalid Date")

            my_facebook_results.append((amount_of_likes, weekday))

        CACHE_DICTION[my_id] = my_facebook_results
        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close()
    return my_facebook_results

# SQL Database
conn = sqlite3.connect("my_facebook_database.sqlite")
curs = conn.cursor()

curs.execute("DROP TABLE IF EXISTS My_Facebook_Table")
curs.execute("CREATE TABLE My_Facebook_Table (Weekday TEXT, Likes NUMBER)")

for each_post in my_facebook_data(emilyinfo.access_token):
    my_tuple = (each_post[1], each_post[0])
    curs.execute('INSERT INTO My_Facebook_Table (Weekday, Likes) VALUES (?,?)', my_tuple)
    conn.commit()

curs.close()
