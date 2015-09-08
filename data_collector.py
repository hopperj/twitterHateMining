#!/usr/bin/python
"""
Author: Jason Hopper
Edited: 2015-04-05

Notes: This code is meant to search twitter for english tweets containing words, slang, or terms
that are hateful, discriminant, racist, etc. These tweets are saved in a MySQL database for further
analysis. Only tweets with the location data are saved. The goal is to look at things like correlation
between hateful words and location.



config file must be similar to (see specific variables below):

[mysql]
user = blah
password = blah
.
.
.

[twitter]
consumer_key = long_string
.
.
.


Databse must have table tweets and have the fields used below such as:
createdAt, text, location, user
currently all fields (including createdAt) are text fields.

"""




import tweepy
from learning import *
from time import sleep
from datetime import datetime, timedelta
import sys, traceback
import MySQLdb as db
from re import sub
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('config.cfg')

con = db.connect( config.get('mysql','address'), config.get('mysql','user'),
                 config.get('mysql','password'), db=config.get('mysql','dbname') )
cur = con.cursor()


auth = tweepy.OAuthHandler(
    config.get('twitter', 'consumer_key'),
    config.get('twitter', 'consumer_secret'),
    )
auth.set_access_token(
    config.get('twitter', 'access_token'),
    config.get('twitter', 'access_token_secret'),
    )

api = tweepy.API(auth)


ret = api.search(q="h", lang="en")

keys = [
    'author',
    'contributors',
    'coordinates',
    'created_at',
    'destroy',
    'entities',
    'favorite',
    'favorite_count',
    'favorited',
    'geo',
    'id',
    'id_str',
    'in_reply_to_screen_name',
    'in_reply_to_status_id',
    'in_reply_to_status_id_str',
    'in_reply_to_user_id',
    'in_reply_to_user_id_str',
    'is_quote_status',
    'lang',
    'metadata',
    'parse',
    'parse_list',
    'place',
    'possibly_sensitive',
    'retweet',
    'retweet_count',
    'retweeted',
    'retweets',
    'source',
    'source_url',
    'text',
    'truncated',
    'user',
]

print '\n'.join( [ str(r.geo)+", "+str(r.place) for r in ret ] )



sys.exit(0)

words = [# A
         # B
         'chink', 'christ killer', # C
         'dego', 'dyke', 'dago', # D
         # E
         'fag', 'faggot', # F
         'gook', 'gringo', 'guido','gay', # G
         # H
         # I
         # J
         'kike', 'kyke', # K
         'lesbian',# L
         # M
         'niglet', 'nigger', # N
         # O
         # P
         # Q
         'raghead', 'roudeye', 'retard', 'retarded', # R
         'slant-eye', 'slant eye', 'slanteye', 'spic', 'spick', 'spik', # S
         'towel head', 'towelhead', # T
         # U
         # V
         'wetback','wigger','wop', # W
         # X
         # Y
         # Z
         ]

term_string = '"%s"'%words[0]
for word in words:
    term_string += ' OR "%s"'%word


t0 = datetime.now()
t1 = datetime.now()
# So we don't get kicked off for being greedy ( currently being set by hand, see bottom )
max_rate = 80 / timedelta(hours=1).total_seconds()

# Can use english words to help select text. Not currently used.
english_words = [ e.strip() for e in open("english_words.txt").readlines() ]
print "Loaded %d english words"%(len(english_words))
eng_count = 0

tweets = []

while 1:
    try:
        t0 = t1
        t1 = datetime.now()
        try:
            results = api.GetSearch(term=term_string, count=100, lang='en')
        except TypeError:
            print "Found an error with values:"
            print traceback.print_exc(file=sys.stdout)
            break
        print "Found %d results."%len(results)
        print "\n\n\n-------------------------------------------------------------------"
        for result in results:
            try:
                result.text = sub("'","",result.text)
                q = "SELECT id FROM tweets WHERE text='%s'"%result.text.encode('ascii', 'ignore')
                cur.execute(q)
                r = cur.fetchone()
                if r is None and result.place is not None:
                    print "Tweet not found in database, moving to add"
                    try:
                        hashtags = ""
                        if len( result.hashtags ) > 0:
                            hashtags = ', '.join( [ str(e) for e in result.hashtags ] )

                        q = "INSERT INTO tweets (createdAt, text, location, user) VALUES('%s', '%s', '%s','%s');"%(
                            result.created_at, result.text.encode('ascii', 'ignore'), result.place['full_name'],
                            result.user.screen_name
                            )
                    except:
                        print "Error building query:"
                        traceback.print_exc(file=sys.stdout)
                        print "-*********************************************"
                        print result.place
                        print result.place['full_name']
                        print result.text
                        print result.created_at
                        print result.id
                        print ', '.join( [ str(e) for e in result.hashtags ] )
                        if len( result.hashtags ) > 0:
                            help(result.hashtags[0])
                        print "*********************************************-"

                    print "\n\n"
                    print result.place['full_name']
                    print result.text
                    print result.created_at
                    print result.id
                    print ', '.join( [ str(e) for e in result.hashtags ] )
                    #print '\n'.join( [ str(e)+"\t"+str( result.AsDict()[e] ) for e in result.AsDict().keys() ] )#.text
                    tweets.append(result)
                    cur.execute(q)
                    con.commit()
                    print "---TWEET ADDED---"
                else:
                    pass#print "Tweet was not unique"


            except TypeError, twitter.TwitterError:
                #traceback.print_exc(file=sys.stdout)
                pass

        #print '\n'.join(api.GetRateLimitStatus()['rate_limit_context']['access_token'])
        #print api.GetRateLimitStatus()
        sleep(30)
        print "\n\n\n\n"
        #print "\n\n"
    except KeyboardInterrupt:
        break
    except:
        print "Printing traceback"
        print "---------------------------------------------------------------"
        traceback.print_exc(file=sys.stdout)
        print "---------------------------------------------------------------"
        print "Exiting data collection."
        #break

con.commit()
con.close()






"""



class Status(__builtin__.object)
 |  A class representing the Status structure used by the twitter API.
 |
 |  The Status structure exposes the following properties:
 |
 |    status.created_at
 |    status.created_at_in_seconds # read only
 |    status.favorited
 |    status.favorite_count
 |    status.in_reply_to_screen_name
 |    status.in_reply_to_user_id
 |    status.in_reply_to_status_id
 |    status.truncated
 |    status.source
 |    status.id
 |    status.text
 |    status.location
 |    status.relative_created_at # read only
 |    status.user
 |    status.urls
 |    status.user_mentions
 |    status.hashtags
 |    status.geo
 |    status.place
 |    status.coordinates
 |    status.contributors




 """
