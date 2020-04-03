from tweepy import StreamListener
from Tweets import *
import Cosine_Sim
from collections import Counter
import json, time, sys,traceback
from datetime import datetime
from email.utils import parsedate_tz, mktime_tz
import os
import glob

class SListener(StreamListener):
    def __init__(self, api,EventDtct):
        self.api = api
        self.EventDtct = EventDtct
        self.writeTime_InHours = 0.5
        self.ClusterActiveTime_InHours = 2.5
        # last time we save the clusters to files
        #self.EventDtct.last_time_print = None
    def on_data(self,data):
        data2 = json.loads(data)
        try:
            user_id = data2['user']['id_str'].encode('ascii','ignore')
            country = ""
            lang = None
            text = ""
            if data2[u'text'] is not None:
                text = (data2[u'text']).encode('ascii','ignore')
            if data2['place'] is not None:
                country = data2['place']['country']
            if data2['lang'] is not None:
                lang = data2['lang']
            if lang == "en" and str.strip(text) != "" and user_id is not None and str.strip(user_id) != "":
                text = text.replace('\n', ' ').replace('\r', '')
                tweet_time = data2['created_at']
                timestamp = mktime_tz(parsedate_tz(tweet_time))
                tweet_time = str(datetime.fromtimestamp(timestamp))
                t = Tweet(text,user_id,tweet_time,country,lang)
                #print t
                self.clusterTweet(t)
        except:
            print "Bad Tweet"
            print traceback.print_exc(file=sys.stdout)
            #return True
        return True
    def on_error(self,status):
        print status
        return True

    def clusterTweet(self,tweet):
        if len(self.EventDtct.clusters) == 0:
            c = Cluster(tweet)
            c.id = str(id(c))+str(int(round(time.time())))
            self.EventDtct.clusters.append(c)
            print "First cluster created !"
        else:
            #find the most similar cluster to add the tweet to it
            print "checking current clusters"
            max_simialiry = 0
            cluster_index = -1
            active_clusters = []
            for i in range(0,len(self.EventDtct.clusters)):
                print "checking cluster ", i , " for time diff"
                if self.isClusterActive(self.EventDtct.clusters[i],self.ClusterActiveTime_InHours):
                    print "cluster was active checkig sim"
                    active_clusters.append(self.EventDtct.clusters[i])
                    cur_sim = self.ClusterTweetSim(self.EventDtct.clusters[i],tweet)
                    if max_simialiry < cur_sim and cur_sim < 1.0:
                        max_simialiry = cur_sim
                        cluster_index = i
            # check if the most similar cluster is above threshold else create new cluster
            print "most similar cluster have sim = ", max_simialiry
            if max_simialiry >= self.EventDtct.dist_threshold and cluster_index != -1:
                self.EventDtct.clusters[cluster_index].addTweet(tweet)
                clusterSize = len(self.EventDtct.clusters[cluster_index].data.index)
                if (self.EventDtct.clusters[cluster_index].userDiversity > self.EventDtct.divers_threshold) and (clusterSize >= 10):
                    self.EventDtct.Events.append(self.EventDtct.clusters[cluster_index])
                    self.writeToEventsFile(self.EventDtct.clusters[cluster_index])
                    print "Event has been detected  !!!!!!!!!!!!!!!!!!!!"
                #else:
                     #print "NOT EVENT !!!!!!!", str(self.EventDtct.clusters[cluster_index].userDiversity), str(len(self.EventDtct.clusters[cluster_index].data.index))
                print "Tweets is added to a current cluster"
            else:
                print "Created new cluster for the tweet"
                c = Cluster(tweet)
                c.id = str(id(c))+str(int(round(time.time())))
                active_clusters.append(c)

            self.EventDtct.clusters = list(active_clusters)
            # decide to write the clusters or not ?
            print "checking whether to write the clusters to the files, clusters count : " , len(active_clusters)
            if self.EventDtct.last_time_print is None and len(self.EventDtct.clusters) >= 50:
                self.writeClusters()
                print "write the clusters for the first time "
            elif self.EventDtct.last_time_print is not None:
                tdelta = datetime.now() - self.EventDtct.last_time_print
                secs = tdelta.total_seconds()
                hours = abs(float(secs / 3600))
                if hours >= self.writeTime_InHours:
                    self.writeClusters()
                    print "write the clusters after write time exceeded"

    def ClusterTweetSim(self,cluster,tweet):
        tweet_txt = tweet.text
        min_similariy = 1.0
        total_sim = 0
        for index, row in cluster.data.iterrows():
            curr_sim = Cosine_Sim.get_cosine(tweet_txt,row['tweet_text'])
            if round(curr_sim,2) >= 0.99:# duplicate tweet
                return 1 # return once you find the duplicate
            else:
                total_sim = total_sim + curr_sim
        #average similarity
        min_similariy = (total_sim*1.0/len(cluster.data.index))
        return round(min_similariy,2)

    # def ClusterTweetSim(self,cluster,tweet):
    #     tweet_txt = tweet.text
    #     min_similariy = 1.0
    #     for index, row in cluster.data.iterrows():
    #         curr_sim = Cosine_Sim.get_cosine(tweet_txt,row['tweet_text'])
    #         if round(curr_sim,2) >= 0.99:# duplicate tweet
    #             return 1 # return once you find the duplicate
    #         elif min_similariy > curr_sim:
    #             min_similariy = curr_sim
    #     return round(min_similariy,2)

    def isClusterActive(self,cluster,active_time_inHours):
        c_active_time = datetime.strptime(cluster.last_activity, '%Y-%m-%d %H:%M:%S')
        time_diff = abs(float((datetime.now()-c_active_time).total_seconds()/3600))
        #print "Time diff for cluster", abs(time_diff) , round(abs(time_diff),2)
        if round(abs(time_diff),2) <= active_time_inHours:
            #print "It is activeeeeeeeeeeeeeeeee"
            # check number of unique users in the cluster are diverse
            clusterSize = len(cluster.data.index)
            if (clusterSize >= 10) and (math.isnan(cluster.userDiversity) or round(cluster.userDiversity,2) <= 0.15):
                # not enought unique users
                return False
            else:
                return True
        else:
            #print "Notttttttttttttttttt activeeeeeeeeeeeeeeeee"
            return False

    def writeClusters(self):
        print "Writing Clusters to a file"
        # delete old clusters
        files = glob.glob("clusters/*.csv")
        for f in files:
            os.remove(f)
        ## write data
        cnt = 1
        for c in self.EventDtct.clusters:
            try:
                st = 'clusters/cluster_'+str(c.id)+'.csv'
                c.data.to_csv(st,index=False,encoding='utf-8')
                cnt = cnt + 1
            except:
                print "Error in writing cluster :::::::::"
                print c.data
                print traceback.print_exc(file=sys.stdout)
        print "Clusters Have been written to files"
        self.EventDtct.last_time_print = datetime.now()

    def writeToEventsFile(self,event_clust):
        print "Writing Events to a file"
        words_list = []
        for index, row in event_clust.data.iterrows():
             words_list += Cosine_Sim.tokenize_only(row['tweet_text'])
        word_counts = Counter(words_list)
        most_common = word_counts.most_common(10)
        text_file = open("events/Events.txt", "a")
        text_file.write("Cluster Id ="+str(event_clust.id)+" ,")
        for word, count in most_common:
           text_file.write("{0} : {1} ,".format(word, count))
        text_file.write("\n")
        text_file.close()
        # write cluster to csv file
        clust_file = 'events/cluster_'+str(event_clust.id)+'.csv'
        if os.path.exists(clust_file):
            os.remove(clust_file)

        try:
            event_clust.data.to_csv(clust_file,index=False,encoding='utf-8')
        except:
            print " Error writing the Event File"




