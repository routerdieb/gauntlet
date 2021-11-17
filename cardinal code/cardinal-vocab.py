import math
import numpy as np

import os
import sys
sys.path.append("..")
sys.path.append("../capture/")
import multiprocessing
import baseVocabCapture
from multiprocessing import Process, Queue
from time import sleep
import time

from Vocabulary import *
from findCardinals import *

# Construction 2
from spacy.lang.en import English
nlp = English()
# Create a Tokenizer with the default settings for English
# including punctuation rules and exceptions
tokenizer = nlp.tokenizer

process_vocabs = []
lock = multiprocessing.Lock()

import re
class card_vocab(baseVocabCapture):
    def preprocess_line(text):
        text = re.sub(r'[\'\",?!]',"",text)
        text = find_card(text)# Just this line is different
        return text



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
    list_objects = []
    for process_id in range(num_processes):
            vocabcapt = card_vocab()
            list_objects.append(vocabcapt)#so we keep a pointer
            p = Process(target=vocabcapt.process_dirs, args=(path,splitted_dirs[process_id],pqueue,andTags,andBase))
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

      