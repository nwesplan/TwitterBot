import pyodbc
import sys
import os
sys.path.append(os.getcwd()+'\\preprocessor')
import preprocessor as p
sys.path.append(os.getcwd() + '\\auth')
import keys as k
import re


cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+k.server+';DATABASE='+k.database+';UID='+k.username+';PWD='+ k.password)
cursor = cnxn.cursor()

#global variables
user_locations_tweet_counter = 0
user_tweet_counter = 0
DUPLICATES = 0

#creates the table name if it does not exist
def create_table(user_name, table_name):
    cursor.execute("if object_id('dbo."+table_name+user_name+"', 'U') is null " +
                   "create table " +table_name + user_name + 
                   """(id_value int IDENTITY(1, 1) PRIMARY KEY,
                   created_at varchar(50),
                   text varchar(1000),
                   source varchar(100),
                   in_reply_to_username varchar(50),
                   retweeted_status varchar(1),
                   user_name varchar(50),
                   user_screen_name varchar(50),
                   user_description varchar(1000),
                   user_location varchar(200),
                   user_followers_count varchar(50),
                   user_friends_count varchar(50),
                   user_favourites_count varchar(50),
                   user_created_at varchar(50),
                   user_verified varchar(50),
                   user_statuses_count varchar(50),
                   place varchar(50),
                   mentions varchar(1000),
                   hashtags varchar(1000)
                   );
                   """) 
    cursor.commit()

#this is not called in the program, its here mainly to save the command    
def create_table_location():
    cursor.execute("""create table USER_LOCATIONS (
                   id_value int IDENTITY(1, 1) PRIMARY KEY,
                   user_screen_name varchar(50),
                   table_name varchar(50),
                   id_string varchar(50),
                   place_type varchar(50),
                   place_name varchar(50),
                   place_full_name varchar(50),
                   place_country varchar(50),
                   place_country_code varchar(50),
                   coordinates_00 varchar(50),
                   coordinates_01 varchar(50),
                   coordinates_10 varchar(50),
                   coordinates_11 varchar(50),
                   coordinates_20 varchar(50),
                   coordinates_21 varchar(50),
                   coordinates_30 varchar(50),
                   coordinates_31 varchar(50)
                   )""")
    cursor.commit()
    
def create_table_mentions(user_name):
    cursor.execute("if object_id('dbo.user_mentions_"+user_name+"','U') is null " +\
                   "create table USER_MENTIONS_"+user_name+""" (
                   id_value int IDENTITY(1, 1) PRIMARY KEY,
                   user_screen_name varchar(50),
                   count_number int
                   )""") 
    cursor.commit()

#finds duplicate rows for timeline tweets
def find_duplicate(dataset, text, user_name, table_name):
    cursor.execute("delete from "+table_name+user_name+" where text = ''")
    cursor.execute("select text from "+table_name+user_name)
    
        
    result_set = cursor.fetchall()
     
    for row in result_set:
        
        if text == row[0]:
            print('found duplicate')
            global DUPLICATES
            DUPLICATES += 1
            print(DUPLICATES)
            return ' '

    sql_query = build_insert_query(dataset, user_name, table_name)
    return sql_query


#This is the main method that processes the json data into valid strings
#it checks and clean tweets for invalid data 
#and populates and formats list for entry into database
def write_stream_data_to_database(data, user_name, table_name, find_duplicates=False):
        
        global DUPLICATES
        
        if DUPLICATES >= 100:
            DUPLICATES = 0
            return -1
        
        
        size = 18
        dataset = [''] * size
  
        json_data = data
        
        #tweet created at time
        dataset[0] = json_data['created_at']
        
        #There are several elements where the actual text in the tweet may exist
        #we want to get the full untruncated text of the tweet so we check each possible element
        #for example if we get the ['text'] of an extended tweet it will contain truncated information
        if not find_duplicates:
            try:
                dataset[1] = json_data['retweeted_status']['extended_tweet']['full_text']
            except KeyError:
                try:
                    dataset[1] = json_data['retweeted_status']['full_text']
                except KeyError:
                    try:
                        dataset[1] = json_data['extended_tweet']['full_text']
                    except KeyError:
                        dataset[1] = json_data['text']
        
        #if in timeline tweets or search tweets
        if find_duplicates:
            try:
                dataset[1] = json_data['retweeted_status']['full_text']
            except KeyError:
                try:
                    dataset[1] = json_data['full_text']
                except KeyError:
                    dataset[1] = json_data['text']
        
        #regular expressions to pull hashtags and mentions from text
        hashtags = re.findall(r"#(\w+)", dataset[1])
        mentions = re.findall(r'(?<!RT\s)@\S+', dataset[1])
        dataset[1] = p.clean(dataset[1])
        
        mentionstring = ''
        hashtagstring = ''
        
        #self cleaning the hashtags and mentions
        for word in hashtags:
            hashtagstring += word + '/'
            
        for word in mentions:
            string = p.clean(word.replace("@", ""))
            string = string.replace("!","")
            string = string.replace('"','')
            string = string.replace(" ","")
            string = string.replace("'", "")
            string = string.replace(".", "")
            string = string.replace("'s", "")
            mentionstring += string + '/'
            
        dataset[16] = mentionstring
        dataset[17] = hashtagstring
        
        #source android/iphone/etc
        dataset[2] = json_data['source']
    
        if 'iPhone' in dataset[2]:
            dataset[2] = 'IPHONE'
        elif 'Android' in dataset[2]:
            dataset[2] = 'ANDROID'
        elif 'Web App' in dataset[2]:
            dataset[2] = 'WEBAPP'
        elif 'iPad' in dataset[2]:
            dataset[2] = 'IPAD'
        elif 'Web Client' in dataset[2]:
            dataset[2] = 'WEBCLIENT'
        elif 'TweetDeck' in dataset[2]:
            dataset[2] = 'TWEETDECK'
        elif 'TweetCaster' in dataset[2]:
            dataset[2] = 'TWEETCASTER'
        elif 'Mobile Web' in dataset[2]:
            dataset[2] = 'MOBILEWEB'
        
        #who this tweet is in reply to
        dataset[3] = json_data['in_reply_to_screen_name']
    
        #retweeted status
        if 'retweeted_status' in json_data:
            dataset[4] = 'T'    
        else:
            dataset[4] = 'F'
         
        #inside user element
        dataset[5] = p.clean(json_data['user']['name'])
        dataset[6] = json_data['user']['screen_name']
        dataset[7] = json_data['user']['description']
        dataset[8] = json_data['user']['location']
        dataset[9] = str(json_data['user']['followers_count'])
        dataset[10] = str(json_data['user']['friends_count'])
        dataset[11] = str(json_data['user']['favourites_count'])   
        dataset[12] = json_data['user']['created_at']   
        dataset[13] = str(json_data['user']['verified'])
        dataset[14] = str(json_data['user']['statuses_count'])
        
        #if the tweet has a place element, we try to get the place information
        try:  
            placelist = ['']  * 16
            placelist[0] = dataset[6]
            placelist[1] = table_name  + user_name
            placelist[2] = str(json_data['place']['id'])
            placelist[3] = str(json_data['place']['place_type'])
            placelist[4] = str(json_data['place']['name'])
            placelist[5] = str(json_data['place']['full_name'])
            placelist[6] = str(json_data['place']['country'])
            placelist[7] = str(json_data['place']['country_code'])
        
            placelist[8] = str(json_data['place']['bounding_box']['coordinates'][0][0][0])
            placelist[9] = str(json_data['place']['bounding_box']['coordinates'][0][0][1])
            placelist[10] = str(json_data['place']['bounding_box']['coordinates'][0][1][0])
            placelist[11] = str(json_data['place']['bounding_box']['coordinates'][0][1][1])
            placelist[12] = str(json_data['place']['bounding_box']['coordinates'][0][2][0])
            placelist[13] = str(json_data['place']['bounding_box']['coordinates'][0][2][1])
            placelist[14] = str(json_data['place']['bounding_box']['coordinates'][0][3][0])
            placelist[15] = str(json_data['place']['bounding_box']['coordinates'][0][3][1])
            
            placelist[5] = format_text_for_db(placelist[5])

            
            sql_query_location = build_insert_query(placelist,'', 'USER_LOCATIONS')
            dataset[15] = str(json_data['place']['id'])
            try:
                global user_locations_tweet_counter
                user_locations_tweet_counter += 1
                print(f'User Location Tweets receieved: {user_locations_tweet_counter}')
                cursor.execute(sql_query_location)
                cursor.commit()
            except pyodbc.DataError as err:
                
                print(sql_query_location)
                print(err)
                
        #no place attribute
        except:          
            dataset[15] = 'F'
        if not find_duplicates:
            dataset[1] = p.clean(dataset[1])
        for x in range(size):
            dataset[x] =  format_text_for_db(dataset[x])
            
        if find_duplicates:
            sql_query = find_duplicate(dataset, dataset[1], user_name, table_name)
        else:
            sql_query = build_insert_query(dataset, user_name, table_name)
                    
        try:

            cursor.execute(sql_query)
            cursor.commit()
            global user_tweet_counter
            user_tweet_counter += 1
            print(f'{user_name} Tweets received: {user_tweet_counter}')
        except pyodbc.DataError as err:
            #error when trying to truncate a field
            print(sql_query)
            print(err)
        
#builds insert statement for user_name and table_name
#calls build_string to build large query statements
def build_insert_query(dataset, user_name, table_name):
    sql_query = "INSERT INTO " + table_name + user_name + " " + \
                "VALUES (" +\
                str(build_string(dataset, "")) +\
                ")"
    return sql_query

#appends the first element of dataset to the string, removes that element and calls itself again
#if there is only 1 element left it finishes up the query and returns the string 
def build_string(dataset, string):
    if len(dataset) > 1:
        string += "'" + dataset[0] + "',"  
        dataset.pop(0)
        return build_string(dataset, string)
    else:
        string += "'" + dataset[0] + "'"
        return string

#removes text that may cause errors writing to database    
def format_text_for_db(text):
    if text is None:
        return 'None'
    try:
        text = str(text.replace(',', ''))
        text = text.replace('\n', ' ')
        text = text.replace(':','')
        return text.replace("'", '')
    except AttributeError:
        return 'None'

