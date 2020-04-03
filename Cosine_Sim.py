import re, math
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer
import nltk
WORD = re.compile(r'\w+')

def get_cosine(text1, text2):
    text1 = " ".join(tokenize_only(text1))
    text2 = " ".join(tokenize_only(text2))
    vec1 = text_to_vector(text1)
    vec2 = text_to_vector(text2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def tokenize_only(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    text = text.replace("&gt;"," ")
    text = text.replace("&lt;"," ")
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    #htmlCodes = ['&#39;','&quot;','&gt;','&lt;','&amp;','&#39','&quot','&gt','&lt','&amp']
    filtered_tokens = []
    stopwords = nltk.corpus.stopwords.words('english')
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    url_index = -1
    for tt in range(0,len(tokens)):
        if re.match('http[s]?', tokens[tt]):
                url_index = tt+2# index+1 = ":" and url is at index+1 of http
                continue
        if re.search('[a-zA-Z]', tokens[tt]) and tokens[tt] not in stopwords and tt!= url_index:
            filtered_tokens.append(tokens[tt])
    return filtered_tokens
