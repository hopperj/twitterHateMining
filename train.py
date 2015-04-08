#!/usr/bin/python

import twitter
from learning import *
from time import sleep
from datetime import datetime, timedelta
import sys, traceback
import MySQLdb as db
from re import sub
import ConfigParser


NB = naivebayes()
NB.load_brain()

con = db.connect(config.get('mysql','address'), config.get('mysql','user'),
                 config.get('mysql','password'), db=config.get('mysql','dbname') )
cur = con.cursor()



q = "SELECT text FROM tweets WHERE classified=0"
cur.execute(q)
data = [ e[0] for e in cur.fetchall() ]


try:
    print "For each, answer: 'Is this negative' [Y/n]"
    train_set = []

    for k in data:
        while 1:
            c = "---"
            print k
            inpt = raw_input("[Y/n]").lower()
            if inpt == "":
                inpt = 'y'
            if inpt == 'y':
                c = "hate"
            else:
                c = "not"
            if c != "---":
                train_set.append((c,k.split()))
                q = "UPDATE tweets SET classified='1' WHERE text='%s'"%(k)
                cur.execute(q)
                con.commit()
                break
except KeyboardInterrupt:
    pass

NB.train(train_set)
print "\n\nFound %d tweets"%len( data )
NB.dump_brain()


