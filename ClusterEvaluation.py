import Cosine_Sim
import pandas as pd
import glob
# files = glob.glob("\clusters_AvgSimilariy\*.csv")
# for f in files:
#     print "working on file , ",f
#     data = pd.read_csv(f,encoding='utf-8')
#     cnt = 1
#     for index, row in data.iterrows():
#         text_file = open(r"\tweets_avg\tweet"+str(cnt)+".txt","w")
#         print "working on tweet ", index
#         words_list = Cosine_Sim.tokenize_only(row['tweet_text'])
#         words_list_str = " ".join(words_list)
#         text_file.write(words_list_str)
#         text_file.close()
#         cnt = cnt + 1


cnt = 1
cluster_ids = []
files = glob.glob("\clusters_AvgSimilariy\*.csv")
for f in files:
    print "working on file , ",f
    data = pd.read_csv(f,encoding='utf-8')
    cnt_str = f+","
    for index, row in data.iterrows():
        text_file = open(r"\tweets_avg\tweet"+str(cnt)+".txt","w")
        print "working on tweet ", index
        words_list = Cosine_Sim.tokenize_only(row['tweet_text'])
        words_list_str = " ".join(words_list)
        text_file.write(words_list_str)
        text_file.close()
        cnt_str = cnt_str + str(cnt)+","
        cnt = cnt + 1
    cluster_ids.append(cnt_str)


text_file = open(r"\tweets_avg\tweet_clusters.txt","w")
for i in cluster_ids:
    text_file.write(i)
    text_file.write("\n")
text_file.close()



