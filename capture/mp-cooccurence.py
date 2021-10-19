import math
import numpy as np
import time

import os
import sys
sys.path.append("..")
import multiprocessing
from multiprocessing import Process, Queue
from math import *

from Vocabulary import *
import cloudpickle


class Co_Occurence_Capturer:

    def __init__(self):
        self.co_occurences = {}
        
    def _assign_entrys(self,word_ids,context_ids,dist,dynWindow):
        if not dynWindow:
            dist = 1.0
        for word_id in word_ids:
                for context_id in context_ids:
                    tuple = (word_id,context_id)
                    if tuple in self.co_occurences:
                        self.co_occurences[tuple] += 1.0 / dist
                    else:
                        self.co_occurences[tuple] = 1.0 / dist


    # Window lenght is one sided length
    # The window is applied on the left and the right.
    # A window size of 0 means, just the focus_word.
    # Article tokens is of type list
    def capture(self,vocab,article_tokens,window_size,dynWindow=True):
        article_ids = []
        for token in article_tokens:
            ids = vocab.get_ids_text(token)
            if ids == []:
                continue
            article_ids.append(ids)
    
        for focus_position,focus_ids in enumerate(article_ids):
            window_left = article_ids[max(0,focus_position-window_size):focus_position]
            for position,context_ids in enumerate(window_left):
                dist = abs(len(window_left) - position)
                self._assign_entrys(focus_ids,context_ids,dist,dynWindow) 
        
            window_right = article_ids[focus_position+1:focus_position+1+window_size]
            for position,context_ids in enumerate(window_right):
                dist = abs(1+ position)
                self._assign_entrys(focus_ids,context_ids,dist,dynWindow)

        return self.co_occurences
    
    def save_coocurrences(self,file_name):
        with open(file_name, 'wb') as file:
            cloudpickle.dump(self.co_occurences, file)
        self.co_occurences = {}

    def load_co_occurence(self,name):
        with open(name, 'rb+') as file:
            self.co_occurences = cloudpickle.load(file)



import re
def preprocess_line(text):
    text = re.sub(r'[\'\".,?!]',"",text)
    return text


push_every_x = 10
def worker(q_files,q_co_oc,vocab,window_size,output_folder,num_processes,is_dyn_window):
    index = 0
    while True:
        while (q_co_oc.qsize() >  num_processes / 2):#slow down
            time.sleep(10)
        
        task = q_files.get()
        #print(str(process_id) + ' still alive')
        if task == 'done':
            q_co_oc.put(capturer.co_occurences)
            q_co_oc.put('done')
            return
        
        print(task)
        with open(task,'r',encoding='utf8') as in_file:
            capturer = Co_Occurence_Capturer()
            in_lines = in_file.readlines()
            for line in in_lines:
                if line.startswith('<doc') or '</doc' in line:
                    pass
                else:
                    line = preprocess_line(line)
                    capturer.capture(vocab,line.split(),window_size,is_dyn_window)
        index += 1
        if (index > 0 and index % push_every_x == 0):
            q_co_oc.put(capturer.co_occurences)
            capturer = Co_Occurence_Capturer()

def save_coocurrences(co_occurence,file_name):
    with open(file_name, 'wb') as file:
        cloudpickle.dump(co_occurence, file)

if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 6:
        raise ValueError('Please provide vocab , wiki-path and window_size and number of processes and output folder and [--taggedVocab] [--noDyn]')
    q_co_oc  = Queue()
    q_files  = Queue()
    path  = sys.argv[2]

    #number = -1
    #for i in range(len(dir_list)):
    #    if dir_list[i] == 'AL':
    #        number = i
    #dir_list = dir_list[number:]
    
    window_size = int(sys.argv[3])
    num_processes = int(sys.argv[4])
    output_folder = sys.argv[5]

    is_tagged = False
    is_dyn_window = True
    if len(sys.argv) > 6:
        if (sys.argv[6] == '--taggedVocab'):
            is_tagged = True
        elif(sys.argv[6] == '--noDyn'):
            is_dyn_window = False
        else:
            raise ValueError('Please provide vocab , wiki-path and window_size and number of processes and output folder and [--taggedVocab] [--noDyn]')
    if len(sys.argv) > 7:
        if (sys.argv[7] == '--taggedVocab'):
            is_tagged = True
        elif(sys.argv[7] == '--noDyn'):
            is_dyn_window = False
        else:
            raise ValueError('Please provide vocab , wiki-path and window_size and number of processes and output folder and [--taggedVocab] [--noDyn]')


    if is_tagged:
        vocab = TaggedVocabulary()
    else:
        vocab = Vocabulary()
    vocab.load(sys.argv[1])

    dir_list = os.listdir(path)
    for directory_name in dir_list:
        file_list = os.listdir(path + '\\' + directory_name)
        for file_name in file_list:
            q_files.put(path + '\\'+directory_name+'\\'+file_name)

    for i in range(num_processes):
        q_files.put('done')

    process_list = []
    for process_id in range(num_processes):
            p = Process(target=worker, args=(q_files,q_co_oc,vocab,window_size,output_folder,num_processes,is_dyn_window))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))
    
    filename = 'co-oc-dict-'
    
    index = 0
    write_every = int(160 / push_every_x)
    finished_processes = 0
    file_index = 0

    co_occurence = {}

    while finished_processes < num_processes:
        print(q_co_oc.qsize(),index % write_every,write_every - 1)

        awnser = q_co_oc.get()
        if (awnser == 'done'):
            finished_processes += 1
        else:
            tmp_co_occurence = awnser
            for token in tmp_co_occurence:
                if token in co_occurence:
                    co_occurence[token] += tmp_co_occurence[token]
                else:
                    co_occurence[token] = tmp_co_occurence[token]

        if index % write_every == write_every - 1 or finished_processes == num_processes:
            save_coocurrences(co_occurence,output_folder + '\\' + 'co-oc-dict-' + str(file_index))
            print('writing')
            co_occurence = {}
            file_index += 1

        index += 1

    
    print('last phase')
    for process in process_list:
        process.join()


