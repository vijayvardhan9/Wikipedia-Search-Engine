import sys
from preprocessing import tokenise, stem, remove_stopwords
import timeit
import re
import math
from collections import defaultdict

# K = 10

# Number of files in the entire dump is 9829059

def findSum(string): 
    weights = {'t':0.4, 'b':0.2, 'i':0.3, 'c':0.05, 'e':0.05}
    Sum = 0
    if 't' in string:
        res = re.search('t[1-9]*', string)
        title_count = int(res.group(0)[1:])
        Sum += title_count * weights['t']
    else:
        title_count = 0

    if 'b' in string:
        res = re.search('b[1-9]*', string)
        body_count = int(res.group(0)[1:])
        Sum += body_count * weights['b']
    else:
        body_count = 0

    if 'i' in string:
        res = re.search('i[1-9]*', string)
        info_count = int(res.group(0)[1:])
        Sum += info_count * weights['i']
    else:
        info_count = 0
    
    if 'c' in string:
        res = re.search('c[1-9]*', string)
        categories_count = int(res.group(0)[1:])
        Sum += categories_count * weights['c']
    else:
        categories_count = 0
    
    if 'e' in string:
        res = re.search('e[1-9]*', string)
        links_count = int(res.group(0)[1:])
        Sum += links_count * weights['e']
    else:
        links_count = 0

    # return title_count, body_count, info_count, categories_count, links_count, Sum
    return Sum
    # return title_count + body_count + info_count + categories_count + links_count

def binary_search_postingList(lines, word, left, right, field = 'd'):
    if right >= left:
        mid = left + (right - left)/2
        mid = int(mid)
        token = lines[mid].split(" ")[0]
        postingsList = lines[mid].split(" ")[1:]
        if token == word:
            res = []
            for i in range(len(postingsList)):
                if field in postingsList[i]:
                    # print(i, postingsList[i], field)
                    # del postingsList[i]
                    res.append(postingsList[i])
            return res
        elif token > word:
            return binary_search_postingList(lines, word, left, mid - 1, field)
        else:
            return binary_search_postingList(lines, word, mid + 1, right, field)
    else:
        return []

def binary_search_title(titles, doc_num, left, right):
    if right >= left:
        mid = left + (right - left)/2
        mid = int(mid)
        file_num = titles[mid].split(" ")[0]
        title = titles[mid].split(" ")[1:]
        file_num = file_num.rstrip('\n')
        if(int(file_num) == int(doc_num)):
            return title
        elif int(file_num) > int(doc_num):
            return binary_search_title(titles, doc_num, left, mid - 1)
        else:
            return binary_search_title(titles, doc_num, mid + 1, right)

def find_title(i):
    temp = len(i)
    if i.find('t') > 0:
        temp = i.find('t')
    elif i.find('b') > 0:
        temp = i.find('b')
    elif i.find('i') > 0:
        temp = i.find('i')
    elif i.find('c') > 0:
        temp = i.find('c')
    elif i.find('e') > 0:
        temp = i.find('e')
    
    doc_num = i[1:temp]
    doc_num.rstrip()
    # for j in titles:
        # if(j.split(" ")[0] == doc_num):
            # return j.split(" ")[1:]
    title = binary_search_title(titles, doc_num, 0, len(titles) - 1)
    return title, doc_num

def find_intersection(postingsLists):
    temp = []
    for postingList in postingsLists:
        temp_list = []
        for doc in postingList:
            for i in range(len(doc)):
                if doc[i] != 'd' and doc[i].isdigit() == False:
                    temp_list.append(doc[:i])
                    break
        temp.append(temp_list)

    def myFunc(n):
        return int(n[1:])

    intersection_list =  list(set(temp[0]).intersection(*temp))
    intersection_list.sort(key = myFunc)
    for i in range(len(postingsLists)):
        temp = []
        for k in intersection_list:
            matching = [s for s in postingsLists[i] if k in s]
            temp.append(matching[0])
        postingsLists[i] = temp
    return postingsLists

def simple_query_ranking(tokens):
    docs = defaultdict(float)
    if len(tokens) == 1:
        # tf_list = []
        first_char = tokens[0][0]
        if first_char.isdigit():
            first_char = 'a'
        file_name = './inverted_index/index_' + first_char + '.txt'
        with open(file_name, 'r') as f:
            lines = f.readlines()
        f.close()
        # for line in lines:
        #     if line.split(" ")[0] == tokens[0]:
        #         postingsList = line.split(" ")[1:]
        postingsList = binary_search_postingList(lines, tokens[0], 0, len(lines))
        if len(postingsList) == 0:
            print("Sorry. This is not a relevant word")
            return {}
        for i in postingsList:
            if i.find('t') > 0:
                temp = i.find('t')
            elif i.find('b') > 0:
                temp = i.find('b')
            elif i.find('i') > 0:
                temp = i.find('i')
            elif i.find('c') > 0:
                temp = i.find('c')
            elif i.find('e') > 0:
                temp = i.find('e')
            field_string = i[temp:]
            # title_count, body_count, info_count, categories_count, links_count, total_count = findSum(field_string)
            total_count = findSum(field_string)
            docs[i[:temp]] = 1 + math.log(total_count)
        sorted_docs = {k: v for k, v in sorted(docs.items(), key=lambda item: item[1], reverse = True)}
        return sorted_docs
    else:
        postingsLists = []
        for token in tokens:
            first_char = token[0]
            if first_char.isdigit():
                first_char = 'a'
            file_name = './inverted_index/index_' + first_char + '.txt'
            with open(file_name, 'r') as f:
                lines = f.readlines()
            f.close()
            postingsList = binary_search_postingList(lines, token, 0, len(lines))
            postingsLists.append(postingsList)
        if len(postingsLists) == 0:
            print("Sorry. This is not a relevant word")
            return {}
        for postingsList in postingsLists:
            for i in postingsList:
                if i.find('t') > 0:
                    temp = i.find('t')
                elif i.find('b') > 0:
                    temp = i.find('b')
                elif i.find('i') > 0:
                    temp = i.find('i')
                elif i.find('c') > 0:
                    temp = i.find('c')
                elif i.find('e') > 0:
                    temp = i.find('e')
                field_string = i[temp:]
                total_count = findSum(field_string)
                tf = 1 + math.log(total_count)
                idf = number_of_files/len(postingsList)
                idf = math.log(idf)
                docs[i[:temp]] += tf * idf
        postingsLists = find_intersection(postingsLists)
        for postingsList in postingsLists:
            for i in postingsList:
                if i.find('t') > 0:
                    temp = i.find('t')
                elif i.find('b') > 0:
                    temp = i.find('b')
                elif i.find('i') > 0:
                    temp = i.find('i')
                elif i.find('c') > 0:
                    temp = i.find('c')
                elif i.find('e') > 0:
                    temp = i.find('e')
                field_string = i[temp:]
                total_count = findSum(field_string)
                tf = 1 + math.log(total_count)
                idf = number_of_files/len(postingsList)
                idf = math.log(idf)
                docs[i[:temp]] += 10 * tf * idf
        sorted_docs = {k: v for k, v in sorted(docs.items(), key=lambda item: item[1], reverse = True)}
        return sorted_docs    

def field_query_ranking(tokens, fields):
    docs = defaultdict(float)
    postingsLists = []
    for i in range(len(tokens)):
        first_char = tokens[i][0]
        if first_char.isdigit():
            first_char = 'a'
        file_name = './inverted_index/index_' + first_char + '.txt'
        with open(file_name, 'r') as f:
            lines = f.readlines()
        f.close()
        postingsList = binary_search_postingList(lines, tokens[i], 0, len(lines), fields[i])
        postingsLists.append(postingsList)
    if len(postingsLists) == 0:
        print("Sorry. This is not a relevant word")
        return {}
    res = postingsLists
    # intersectionLists = find_intersection(postingsLists)
    if len(postingsLists[0]) == 0:
        postingsLists = res
    for postingsList in postingsLists:
        for i in postingsList:
            if i.find('t') > 0:
                temp = i.find('t')
            elif i.find('b') > 0:
                temp = i.find('b')
            elif i.find('i') > 0:
                temp = i.find('i')
            elif i.find('c') > 0:
                temp = i.find('c')
            elif i.find('e') > 0:
                temp = i.find('e')
            field_string = i[temp:]
            total_count = findSum(field_string)
            tf = 1 + math.log(total_count)
            idf = number_of_files/len(postingsList)
            idf = math.log(idf)
            docs[i[:temp]] += tf * idf
    intersectionLists = find_intersection(postingsLists)
    for intersectionList in intersectionLists:
        for i in intersectionList:
            if i.find('t') > 0:
                temp = i.find('t')
            elif i.find('b') > 0:
                temp = i.find('b')
            elif i.find('i') > 0:
                temp = i.find('i')
            elif i.find('c') > 0:
                temp = i.find('c')
            elif i.find('e') > 0:
                temp = i.find('e')
            field_string = i[temp:]
            total_count = findSum(field_string)
            tf = 1 + math.log(total_count)
            idf = number_of_files/len(intersectionList)
            idf = math.log(idf)
            docs[i[:temp]] += 10 * tf * idf
    
    sorted_docs = {k: v for k, v in sorted(docs.items(), key=lambda item: item[1], reverse = True)}
    # print(sorted_docs)
    return sorted_docs

def begin_search():
    f = open('./inverted_index/fileNumber.txt', 'r')
    global number_of_files
    number_of_files = int(f.read().strip())
    f.close()

    query_file = sys.argv[1]
    with open(query_file, 'r') as q:
        queries = q.readlines()
    data = ""
    for query in queries:
        global K
        K = query.split(', ')[0]
        K = int(K)
        query = query.split(', ')[1:]
        temp_query = ''
        for i in query:
            temp_query += i + ' '
        query = temp_query
        query = query.lower()
        start = timeit.default_timer()
        if re.match(r'[t|b|i|c|l]:', query):
            tempFields = re.findall(r'([t|b|c|i|l]):', query)
            words = re.findall(r'[t|b|c|i|l]:([^:]*)(?!\S)', query)
            # print(tempFields, words)
            fields,tokens = [],[]
            si = len(words)
            i=0
            while i<si:
                for word in words[i].split():
                    fields.append(tempFields[i])
                    tokens.append(word)
                i+=1
            tokens = remove_stopwords(tokens)
            tokens = stem(tokens)
            # print(fields, tokens)
            results = field_query_ranking(tokens, fields)
            # print(results)
            
        else:
            tokens = tokenise(query)
            tokens = remove_stopwords(tokens)
            tokens = stem(tokens)
            results = simple_query_ranking(tokens)
            # print(results)
        if len(results) > 0:
            results = sorted(results, key=results.get, reverse=True)
            if(len(results) > K):
                results = results[:K]
            for key in results:
                key.rstrip()
                title, title_doc_num = find_title(key)
                data += title_doc_num
                data += ', '
                # print(title_doc_num, end = ' ')
                if title is not None:
                    for i in title:
                        data += i + ' '
                        # print(i, end = ' ')
                    data = data[:-1]
        else:
            data += "No results found! Try modifying the search by reducing the length maybe?\n"
        end = timeit.default_timer()
        data += str(end - start) + ', '
        data += str((end - start)/K)
        data += '\n\n'
        # print('\n')
    # print('data', data)
    with open('queries_op.txt', 'w') as f:
        f.write(data)
    # print("Time taken = ", end - start, "\n")

if __name__ == '__main__':
    with open('./inverted_index/title.txt', 'r') as title_file:
        titles = title_file.readlines()
    begin_search()