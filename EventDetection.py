import datetime
import time
from email.utils import parsedate_tz, mktime_tz
import tweepy
import sys,traceback
import json
import glob
from Slistener import SListener
from Tweets import *
import pandas as pd

ckey ="your key"
csecret = "your secret"
atoken = "access token"
asecret = "access secret"
auth = tweepy.OAuthHandler(ckey,csecret)
auth.set_access_token(atoken,asecret)
api = tweepy.API(auth)

class EventsDetector:
    def __init__(self,dist_threshold,divers_threshold):
        self.Events = []
        self.clusters = []
        self.dist_threshold = dist_threshold
        self.divers_threshold = divers_threshold
        self.interrupted = 1
        self.last_time_print= None
        ##
        self.track_keywords = ['earthquake','tsunami','Tornadoe','volcano','thunderstorm','cyclone']


    def startDetection(self):
        while True:
            if self.interrupted == 1:
                self.loadClusters()
                self.interrupted = 0
                "Enterd Interrupted"
            listen = SListener(api,self)
            stream = tweepy.Stream(auth, listen)
            print "Streaming started..."
            try:
                print len(self.clusters), " is the number of cluster at the begining"
                stream.filter(track = self.track_keywords)
            except KeyboardInterrupt:
                stream.disconnect()
                self.writeClustersBeforeExit()
                print 'My application is ending!'
                break
            except:
                print "Unexpected error:", sys.exc_info()
                print traceback.print_exc(file=sys.stdout)
                self.writeClustersBeforeExit()
                print " CRETED FILES"
                self.interrupted = 1
                #print "error!"
                #stream.disconnect()

    def loadClusters(self):
        self.clusters = []
        for f in glob.glob("clusters/*.csv"):
            print "reading now"
            dt = pd.read_csv(f,encoding='utf-8')
            c_id = f.split("_")[1]# get id.csv
            c_id = c_id.split(".")[0]#remove .csv
            if len(dt.index) > 0:
                print "read is done"
                c = Cluster(id=c_id)
                c.data = dt
                #print dt
                c.userDiversity = c.cal_userDiversity()
                max_time = max(c.data.apply(lambda x: datetime.datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'), axis=1))
                c.last_activity = (max_time).strftime('%Y-%m-%d %H:%M:%S')
                print c.last_activity
                self.clusters.append(c)

    def writeClustersBeforeExit(self):
        cnt = 1
        for c in self.clusters:
            st = 'clusters/cluster_'+str(c.id)+'.csv'
            c.data.to_csv(st,index=False,encoding='utf-8')
            cnt = cnt + 1
        print "Clusters Have been written to files"


def main():
    print "hello"
    e = EventsDetector(0.7,0.9)
    e.startDetection()
    print "Done"

if __name__ == "__main__":
    main()