import sys

sys.path.append('C:\\Users\\nwesp\\Spyder3Projects\\Twitter\\auth')
import keys
import pyodbc
import tweepy
import json
import Database

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+keys.server+';DATABASE='+keys.database+';UID='+keys.username+';PWD='+keys.password)
cursor = cnxn.cursor()

#extend tweepy Stream Listener
class TweetListener(tweepy.StreamListener):
    
    def __init__(self, api, user_name, limit=1_000_000):
        print(limit)
        self.tweet_count = 0
        self.TWEET_LIMIT = limit
        self.user_name = user_name
        super().__init__(api) 

    def on_connect(self):
        print('Connection successful\n')
    
    #this method is called from the superclass in a while loop
    def on_data(self, data):
        #load json data
        json_data = json.loads(data)
        #write to database
        Database.write_stream_data_to_database(json_data, self.user_name, 'user_tweets_')
        
        #print(f'{self.user_name} Tweets received: {self.tweet_count}')
        self.tweet_count += 1
        return self.tweet_count != self.TWEET_LIMIT
    def get_key(self):
        print()
    def on_error(self, status):
        print(repr(status))
        return True
    def on_status(self, status):
        print(status.text)


