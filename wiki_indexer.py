import xml.sax
import sys
import subprocess
from collections import defaultdict
import re
import Stemmer
import os
import time
from preprocessing import tokenise, stem, remove_stopwords

start_time = time.time()
total_tokens = 0
docID = {}
page_count = 0
file_count = 0
offset = 0
PostingsList = defaultdict(list)
FinalPostingsList = defaultdict(list)

def create_frequency_dict(data, words):
    d = {}
    for word in data:
        if(d.get(word) == None):
            d[word] = 1
        else:
            d[word] += 1
        if(words.get(word) == None):
            words[word] = 1
        else:
            words[word] += 1
    return d, words

def processText(text, title):
    # Links and categories are below references. 
    # Title, text, info are above references.
    
    ref = "== references =="
    ref2 = "==references=="
    text = text.lower()
    temp = text.split(ref)

    if len(temp) == 1:
        temp = text.split(ref2)
    if len(temp) == 1: # There are no links and categories
        links = []
        categories = []
    else:
        categories = processCategories(temp[1]) # Send below part of references
        links = processLinks(temp[1])
    body = processBody(temp[0])
    title = processTitle(title)
    info = processInfo(temp[0])

    return title, body, info, categories, links

def processTitle(title):
    # print('Title before', title)
    title = title.lower()
    title = tokenise(title)
    title = remove_stopwords(title)
    title = stem(title)
    # print('Title: ', title)
    return title

def processBody(text):
    # print('Body: ',text)
    data = re.sub(r'\{\{.*\}\}', r' ', text)
    data = tokenise(data)
    data = remove_stopwords(data)
    data = stem(data)
    # print('Body: ',data)
    return data

def processInfo(text):
    data = text.split('\n')
    flag = -1
    info = []
    st="}}"
    for line in data:
        if re.match(r'\{\{infobox', line):
            info.append(re.sub(r'\{\{infobox(.*)', r'\1', line))
            flag = 0
        elif flag == 0:
            if line == st:
                flag = -1
                continue
            info.append(line)
    data = tokenise(' '.join(info))
    data = remove_stopwords(data)
    data = stem(data)
    # print("Info: ", data)   
    return data

def processLinks(text):
    data = text.split('\n')
    links = []
    for line in data:
        if re.match(r'\*[\ ]*\[', line):
            links.append(line)
    data = tokenise(' '.join(links))
    data = remove_stopwords(data)
    data = stem(data)
    # print('Links: ', )
    return data

def processCategories(text):
    data = text.split('\n')
    categories = []
    for line in data:
        if re.match(r'\[\[category', line):
            categories.append(re.sub(r'\[\[category:(.*)\]\]', r'\1', line))
    data = tokenise(' '.join(categories))
    data = remove_stopwords(data)
    data = stem(data)
    # print('Categories: ', data)
    return data

def writeToFile(PostingsList, docID, file_count, offset):
    d_offset = []
    data = []
    page_offset = offset
    for key in sorted(docID):
        temp = str(key) + ' ' + docID[key].strip()
        if(len(temp) > 0):
            page_offset += 1 + len(temp)
        else:
            page_offset += 1
        data.append(temp)
        d_offset.append(str(page_offset))
    file_name = './20171308/inverted_index/titleOffset.txt'
    if os.path.exists(file_name):
        writing_type = 'a'
    else:
        writing_type = 'w'
    with open(file_name, writing_type) as f:
        f.write('\n'.join(d_offset))
        f.write('\n')
    
    file_name = './20171308/inverted_index/title.txt'
    if os.path.exists(file_name):
        writing_type = 'a'
    else:
        writing_type = 'w'
    
    with open(file_name, writing_type) as f:
        f.write('\n'.join(data))
        f.write('\n')
    
    data = []

    # for key in sorted(PostingsList.keys()):
    #     postings = PostingsList[key]
    #     string = key + ' '
    #     string = string + ' '.join(postings)
    #     data.append(string)
    
    # file_path = './20171308/inverted_index/index'
    # file_name = file_path + str(file_count) + '.txt'
    # with open(file_name, 'w') as f:
    #     f.write('\n'.join(data))
    
    return page_offset

def file_handler(index, docID, out_path):
    data = []
    data1 = []
    next_char = 'a'
    for key in sorted(index.keys()):
        string = key + ' '
        postings = index[key]
        string += ' '.join(postings)
        first_char = string[0]
        if first_char != next_char and not first_char.isdigit():
            file_name = './20171308/inverted_index/index_' + next_char + '.txt'
            with open(file_name, 'w') as f:
                f.write('\n'.join(data))
            data = []
            next_char = chr(ord(next_char) + 1)
        data.append(string)
        data1.append(string)
    file_name = './20171308/inverted_index/index_' + next_char + '.txt'
    with open(file_name, 'w') as f:
        f.write('\n'.join(data))
    data = []
    # file_input = out_path 
    file_name = out_path
    if os.path.exists(file_name):
        writing_type = 'a'
    else:
        writing_type = 'w'
    with open(file_name, writing_type) as f:
        f.write('\n'.join(data1))
    # with open(file_input, 'w') as f:
        # f.write('\n'.join(data))
    
    with open(sys.argv[3], 'a') as f:
        f.write(str(len(FinalPostingsList)))
        f.write('\n')

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.title = ''
        self.text = ''
        self.current_tag = None
        self.id_flag = 0
        self.ID = ''
        self.buffer = None
        self.total_tokens = 0

    def Indexer(self, title, body, info, categories, links):
        global page_count, file_count, PostingsList, docID, offset, FinalPostingsList
        ID = page_count
        words = {}
        links, words = create_frequency_dict(links, words)
        title, words = create_frequency_dict(title, words)
        info, words = create_frequency_dict(info, words)
        body, words = create_frequency_dict(body, words)
        categories, words = create_frequency_dict(categories, words)

        for word, key in words.items():
            string = 'd' + str(ID)
            if title.get(word):
                string += 't' + str(title[word])
            if body.get(word):
                string += 'b' + str(body[word])
            if info.get(word):
                string += 'i' + str(info[word])
            if categories.get(word):
                string += 'c' + str(categories[word])
            if links.get(word):
                string += 'e' + str(links[word])
            PostingsList[word].append(string)
            FinalPostingsList[word].append(string)
        
        page_count += 1
        if page_count % 5000 == 0:
            offset = writeToFile(PostingsList, docID, file_count, offset)
            PostingsList = defaultdict(list)
            docID = {}
            file_count += 1

    def startElement(self, tag, attributes):
        if tag == 'id' and self.id_flag == 0:
            self.id_flag = 1
        self.current_tag = tag
        
    def characters(self, content):
        if self.current_tag == 'title':
            self.title += content
        elif self.current_tag == 'text' and self.id_flag == 0:
            self.text = self.text + content
        elif self.current_tag == 'id' and self.id_flag == 1:
            self.ID = content
            self.id_flag = 0

    def endElement(self, tag):
        if tag == 'id':
            self.id_flag = 0
            self.current_tag = 'text'
        if tag == 'page':
            global docID, page_count
            docID[page_count] = self.title.strip().encode("ascii", errors = 'ignore').decode()
            title, body, info, categories, links = processText(self.text, self.title)
            self.total_tokens += len(title) + len(body) + len(info) + len(categories) + len(links)
            self.Indexer(title, body, info, categories, links)
            self.title = ''
            self.text = ''
            self.current_tag = None
            self.flag = 0
            self.ID = ''
            self.buffer = None
    
    def endDocument(self):
        with open(sys.argv[3], 'w') as f:
            f.write(str(self.total_tokens))
            f.write('\n')
        
class Parser():
    def __init__(self, file):
        self.parser = xml.sax.make_parser()
        self.handler = WikiXmlHandler() 
        self.parser.setContentHandler(self.handler)
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.parse(file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 wiki_indexer.py xml_data.xml ./output output_stat.txt")
        sys.exit()

    print("Please wait! It'll take around 4-5 minutes for indexing the wiki dump")
    parser = Parser(sys.argv[1])
    docID = {}

    dir_name = sys.argv[2]
    temp_name = './20171308/inverted_index/fileNumber.txt'
    with open(temp_name, 'w') as f:
        f.write(str(page_count))
    
    offset = writeToFile(PostingsList, docID, file_count , offset)
    file_handler(FinalPostingsList, docID,'./20171308/inverted_index/index.txt')
    PostingsList = defaultdict(list)
    docID = {}
    file_count = file_count + 1
    print("Time taken: ", time.time() - start_time, " seconds")
