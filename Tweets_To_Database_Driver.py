import tweepy
import sys
import os

import keys
import time
import pandas as pd
from Tweets_To_Database import TweetListener
import Database


def main():
    
    #Tweepy authentication
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    print('Type back at any point or exit in the main menu to quit.')
    while True:
        #user input
        enter = input('1: Stream tweets about user to database (limited to 100 tweets)\n' +\
                      '2: Stream tweets using csv file (limited to 100 tweets)\n' +\
                      '3: Custom Search (limited to 100 tweets)\n' +\
                      '4: Load user tweets into database from timeline (This may take up to 20 minutes)\n'
                      )
                                
        if enter == 'exit':
            exit()
        if enter == '1':
            stream(api)
        elif enter == '2':
            streamloop_csv(api)
        elif enter == '3':
            search(api)
        elif enter == '4':
            timeline(api)

#main method for searching tweets
def search(api):
    
    search_criteria = str(input('Enter search criteria: '))
    if search_criteria == 'back':
        return
    tweets = api.search(q=search_criteria, count=10000)
    search_criteria_ = search_criteria.replace(' ', '_')
    #create table
    Database.create_table(search_criteria_, 'search_tweets_')
    #iterate through tweets and write to database
    for tweet in tweets:
        Database.write_stream_data_to_database(tweet._json, search_criteria_,
                                               'search_tweets_', find_duplicates=True)
#main method for timeline tweets
def timeline(api):
    name = '0'
    while name != 'back':
        name = str(input('Enter username to retrieve timeline data for:'))
        if name == 'back':
            return
        #get user info, make sure user name is valid
        name_id = getuserinfo(api, name, 'timeline_tweets_')
        if name_id == '0':
            return
        x = 0
        #iterate through tweepy cursor object and write to database
        for status in tweepy.Cursor(api.user_timeline, screen_name=name,
                                    tweet_mode="extended").items():
            returnint = Database.write_stream_data_to_database(status._json, name,
                                                   'timeline_tweets_', find_duplicates=True)
            if returnint == -1:
                return
                
#main method for streaming tweets             
def stream(api):
    name = ''
    name_id = '0'
    limit = 1_000_000
    while name != 'back':
        name = ''
        name_list = []
        name = str(input('Enter username to stream for:'))
        name_list = name.split(' ')
        if name_list[0] == 'back':
            return
        #optional parameters. user can enter just the username
        #or the username and a suffix to the database
        #or username and the tweet limit
        #or username suffix and tweet limit
        if len(name_list) > 3:
            print('\n')
            return
        if len(name_list) == 1:
            name_list.append('')
            name_list.append('100')
        elif len(name_list) == 2:
            if not name_list[1].isdigit():
                name_list.append('100')
            else:
                amount = name_list[1]
                name_list[1] = ''
                name_list.append(amount)
        if not name_list[2].isdigit():
            return

        
        #make sure username is valid
        name_id = getuserinfo(api, name_list[0], 'user_tweets_', suffix=name_list[1])
        if name_id == '0':
            return
        #call stream loop
        streamloop(api, name_list[0], str(name_id), tweetlimit=int(name_list[2]), extension=name_list[1])
        
#stream tweets to db can cause errors,
# if user enters 1 million or more for tweet limit, the program will continue past errors
def streamloop(api, username, userid, tweetlimit=1_000_000, extension=''):
    stream_tweets_to_db(api, username, userid, tweetlimit, extension)
    while tweetlimit >= 1_000_000:
        stream_tweets_to_db(api, username, userid, tweetlimit, extension)
     
def streamloop_csv(api):
    input = True
    while input:
        input = run_tweet_stream_csv(api)
    
#main method for csv streaming
def run_tweet_stream_csv(api):
    #cap at 100 for testing purposes
    tweet_limit = 1_00
    filename = input('Enter file name:')
    if filename == 'back':
        return False
    #return to main menu if invalid csv file entered
    try:
        userhandle = pd.read_csv(filename)
    except:
        print('Error reading file. Returning to main menu.\n')
        return False
    filename = filename.rstrip('.csv')
    
    #grab twitter ids from csv file
    userhandle['TwitterID'] = userhandle['TwitterID'].astype(int).astype(str)
     
    #create table and intialize stream using Tweets_To_Databse TweetListener subclass
    Database.create_table(filename, 'user_tweets_')
    twitter_stream = tweepy.Stream(api.auth, TweetListener(api, filename, tweet_limit))
    
    #starts the stream, calls TweetListener's on_data method
    try:
        twitter_stream.filter(track=userhandle.TwitterHandle.tolist(),
                      follow=userhandle.TwitterID.tolist())
    except Exception as e:
        print("Fatal exception caught.")
        print(e)
        print("Restarting stream...")
        time.sleep(1)
        
        
def stream_tweets_to_db(api, user, user_id, tweetlimit=1_000_000, suffix=''):

    userid = []
    userid.append(user_id)

    userhandle = []
    userhandle.append(user)

    twitter_stream = tweepy.Stream(api.auth, TweetListener(api, user+suffix, limit=tweetlimit), tweet_mode='extended')
    
    try:
        twitter_stream.filter(track=userhandle, follow=userid)
    except Exception as e:
        print("Fatal exception caught.")
        print(e)
        print("Restarting stream...")
        time.sleep(1)

#method for checking if the username exists, creates a table if username does exist      
def getuserinfo(api, name, table_name, suffix=''):
    try:
        account_name = api.get_user(name)    
    except tweepy.error.TweepError:
        print('Username not found.')
        return '0'
    else:
        print(name+suffix)
        Database.create_table(name+suffix, table_name)
        return account_name.id   

main()