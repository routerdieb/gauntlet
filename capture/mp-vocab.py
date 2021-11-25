import math
import numpy as np

import os
import sys
sys.path.append("..")
import multiprocessing
from multiprocessing import Process, Queue
from time import sleep
import time

from Vocabulary import *

# Construction 2
from spacy.lang.en import English
nlp = English()
# Create a Tokenizer with the default settings for English
# including punctuation rules and exceptions
tokenizer = nlp.tokenizer

process_vocabs = []
lock = multiprocessing.Lock()

import re

def preprocess_line(text):
    text = re.sub(r'[\'\",?!]',"",text)
    return text

def process_dirs(path,dir_list,queue,andTags,andBase):
    if (andTags):
        vocab = TaggedVocabulary(includeWords_wo_Tags=andBase)
    else:
        vocab = Vocabulary()
    for directory_name in dir_list:
        print(directory_name)
        for file_name in os.listdir(path + "/" + directory_name):
            file_path = os.path.join(path, directory_name,file_name)
            with open(file_path,'r',encoding='utf8') as in_file:
                in_lines = in_file.readlines()
                for line in in_lines:
                    if line.startswith('<doc') or line.startswith('</doc') or line.startswith(' </doc'):
                        pass
                    else:
                        line = preprocess_line(line)
                        vocab.build_from_text(line.split())
    queue.put(vocab) 
                    

if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise ValueError('Please provide preprocessed wikipath and filename of vocabulary and number of processes [--andTags][--andBase]')
    pqueue = Queue()
    path = sys.argv[1]
    save_file = sys.argv[2]
    print(path)
    dir_list = os.listdir(path)
    
    num_processes = int(sys.argv[3])
    
    andTags = False
    andBase = False
    i = 4
    while len(sys.argv) > i:
        if (sys.argv[i] == '--andTags'):
            andTags = True
        elif sys.argv[i] == '--andBase':
            andBase = True
        else:
            raise ValueError('Please provide preprocessed wikipath and filename of vocabulary and number of processes [--andTags]')
        i += 1

    splitted_dirs = []
    for process in range(num_processes):
        splitted_dirs.append([])
    for dir_index in range(len(dir_list)):
        dir = dir_list[dir_index]
        splitted_dirs[dir_index % num_processes].append(dir)
    
    process_list = []

    startTime = time.time()
    for process_id in range(num_processes):
            p = Process(target=process_dirs, args=(path,splitted_dirs[process_id],pqueue,andTags,andBase))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))

    for result_index in process_list:
        process_vocabs.append(pqueue.get())
    
    for process in process_list:
        process.join()
    if andTags:
        global_vocabulary = TaggedVocabulary()
    else:
        global_vocabulary = Vocabulary()
    for vocab in process_vocabs:
        print(vocab.get_size())
        for word in vocab.word_frequency:
            if word in global_vocabulary.word_frequency:
                global_vocabulary.word_frequency[word] += vocab.word_frequency[word]
            else:
                global_vocabulary.word_frequency[word] = vocab.word_frequency[word]
    

    global_vocabulary.save('../vocabs/unfiltered' + save_file)
    print(global_vocabulary.get_size())
    global_vocabulary.filter_just_symbol_tokens()
    print(global_vocabulary.get_size())
    global_vocabulary.filter(100)
    print(global_vocabulary.get_size())
    global_vocabulary.filterWord(''+chr(4))
    print(global_vocabulary.get_size())
    global_vocabulary.assignIds()
    print('global_vocabulary_post_filtering')
    print(global_vocabulary.get_size())
    global_vocabulary.save('../vocabs/' + save_file)

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))

      