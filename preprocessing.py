import re
import Stemmer
from collections import defaultdict

with open('./stopwords.txt', 'r') as file :
    stop_words = set(file.read().split('\n'))
    stop_dict = defaultdict(int)
    for word in stop_words:
    	stop_dict[word] = 1

def tokenise(text):
    text = text.encode("ascii", errors="ignore").decode()
    text = re.sub(r'[^A-Za-z0-9]+', r' ', text)
    return text.split()

def remove_stopwords(text):
    return [word for word in text if stop_dict[word] != 1]

def stem(text):
    stemmer = Stemmer.Stemmer('english')
    return stemmer.stemWords(text)