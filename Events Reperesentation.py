from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
import Cosine_Sim
# import time
#
#
# from pytagcloud import create_tag_image, make_tags
# from pytagcloud.lang.counter import get_tag_counts




# events_file=r'C:\\Users\DELL\Desktop\Events.txt'
#
# for line in open(events_file):
#     line_list = ((line.rstrip("\n")).split(","))
#     words= line_list[1:len(line_list)]
#     print(words)
#     all_w = ""
#     for w in words:
#         ws = w.split(":")
#         if len(ws) == 2:
#             ws1 = ws[0].strip()
#             ws1=((ws1.upper()+" ")*int(ws[1].strip())).strip()
#             print(ws1)
#             all_w = all_w+" "+ws1
#     print all_w
#     print "/////////////////////////////////////////////////"
    # wordcloud = WordCloud(stopwords=STOPWORDS,
    #                       background_color='white',
    #                       width=1200,
    #                       height=1000
    #                      ).generate(all_w)


    # plt.imshow(wordcloud)
    # plt.axis('off')
    # plt.show()


events_file=r'\cluster_1068241281461860958.csv'
dt = pd.read_csv(events_file,encoding='utf-8')
words_list = []
for index, row in dt.iterrows():
    words_list += Cosine_Sim.tokenize_only(row['tweet_text'])

for i in words_list:
    print (i).encode('ascii','ignore')

print "/////////////////////////////////////////////////"
