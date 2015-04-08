#    Copyright (C) 2009-2011 Jason T. Hopper
#    All rights reserved.
#  
#    Jason T. Hopper <hopperj@dal.ca>
#    Alice Research Group
#    1271 Church Street, Apt 713. Halifax, Nova Scotia, B3J 3L3  
#
#    ALICE is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    ALICE is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/bin/python

import re
import math
from random import seed
from random import random
from math import tanh
from math import sqrt
import cPickle as pickle
import MySQLdb as db



class naivebayes:
    def __init__(self,default='chat',thresh=1.0,verbose=0, dbAddress="", dbUsername="", dbPasswd="", dbName=""):
        # brain = [ [classification, [list, of, words] ] 
        self.brain = []
        self.default_classification = default
        self.thresh = thresh
        self.verbose = verbose
        self.con = db.connect(dbAddress, dbUsername, dbPasswd, db=dbName)
        self.cur = con.cursor()



    def load_brain(self):
        self.brain = pickle.load( open("hate.pickle", 'rb') )
        q = "SELECT text,location,user,classification FROM classified_tweets"
        self.cur.execute(q)
        self.brain = [ [e[0],e[-1].split(',')] for e in self.cur.fetchall() ]
    
    def dump_brain(self):
        pickle.dump( self.brain, open("hate.pickle", 'wb') )
        
    def classify(self,items):
        probs = {}
        max_p = ['hate',0.0]
        for cat,inpt in self.brain:
            p = 1.0
            # This value is used twice, so just calculate it once.
            # It is the number of times this class appears            
            tmp = float(len([c for c,i in self.brain if c == cat]))
            pc = tmp / float(len(self.brain))            
            for w in items:
                if self.verbose:
                    print "Comparing",w," and",inpt,"\t", \
                        ( (len([ c for c,t in self.brain if w in t and c == cat])) / tmp + 1.0 )
                p *= ( (len([ c for c,t in self.brain if w in t and c == cat])) / tmp + 1.0 )
            if p == 1.0:
                p = 0.0
            else:
                # Normalize results based on the total number of features
                # each classification has, so that classes with only a few
                # important features don't get drowned out by larger sets.
                p = p * pc / self.get_total_class_features(cat) * 1000.0
            if probs.get(cat,0.0) < p:
                probs[cat] = p
            if max_p[1] < p:
                max_p = [cat,p]
        if self.verbose:
            print "Printing classification results!"
            for k,v in probs.items():
                print k,"\t",v
        # Make sure that the selected classification is at least
        # some amount above the next highest.
        for k,v in probs.items():
            if k == max_p[0]:
                continue
            #print "%s/%s:\t%f"%(k,max_p[0],v/max_p[1])
            if max_p[1] < self.thresh*v:
                print "There was another classification that was close enough to raise doubt"
                return self.default_classification
        return max_p[0],probs


    def get_total_class_features(self,cat):
            tot_f = 0
            for c,i in self.brain:
                if c == cat:
                    tot_f += len(i)
            return float(tot_f)


    def makeLower(self):
        for i,v in enumerare( self.brain ):
            self.brain[i] = [ v[0], [ d.lower() for d in v[1] ] ]
                
    def train(self,train_set):
        # Must be given a list with elements being:
        # [ classification, [ list, of, words ]
        for c,i in train_set:
            if i not in [ [ d.lower() for d in e[1] ] for e in self.brain ]:
                self.brain.append([c,i])
            else:
                for j,v in enumerate(self.brain):
                    if v[1] == i:
                        self.brain[j] = [c,i]


