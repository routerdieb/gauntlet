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

messageParameters = 'Please provide vocab , wiki-path and window_size and number of processes and output folder and  [--noDyn] [--writesize XYZ] [--pushevery XY][--asymetrical][--continueFromOld]'



import re
def preprocess_line(text):
    text = re.sub(r'[\'\",?!\.]',"",text)
    text = re.sub('['+chr(4)+']sp',"",text)
    text = re.sub('['+chr(4)+']space',"",text)
    text = re.sub(r'[ ]{2,}',' ',text)
    return text


def worker(push_every_x,q_files,q_co_oc,vocab,window_size,num_processes,is_dyn_window,is_asymetrical):
    index = 0
    capturer = None
    while True:
        while (q_co_oc.qsize() >  num_processes / 2):#slow down
            time.sleep(10)
        
        task = q_files.get()
        #print(str(process_id) + ' still alive')
        if task == 'done':
            if capturer:
                q_co_oc.put(capturer.co_occurences)
            q_co_oc.put('done')
            return
        
        print(task)
        with open(task,'r',encoding='utf8') as in_file:
            if not capturer:
                capturer = Co_Occurence_Capturer(dynWindow=is_dyn_window)
            in_lines = in_file.readlines()
            for line in in_lines:
                if line.startswith('<doc') or '</doc>' in line[0:100]:
                    pass
                else:
                    line = preprocess_line(line)
                    capturer.capture(vocab,line.split(),window_size)
        if (index % push_every_x == push_every_x - 1):
            q_co_oc.put(capturer.co_occurences)
            capturer = Co_Occurence_Capturer(dynWindow=is_dyn_window)

        index += 1

def save_coocurrences(co_occurence,file_name):
    with open(file_name, 'wb') as file:
        cloudpickle.dump(co_occurence, file)

if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 6:
        raise ValueError(messageParameters)
    q_co_oc  = Queue()
    q_files  = Queue()
    path  = sys.argv[2]

    
    
    window_size = int(sys.argv[3])
    num_processes = int(sys.argv[4])
    output_folder = sys.argv[5]

    print("the window size is " + str(window_size))
    print("the number of proceses is " + str(num_processes))

    # defaults
    collet_x_before_write = 100
    push_every_x = 10
    is_dyn_window = True
    is_asymetrical = False
    continueFromOld = False

    i = 6
    while len(sys.argv) > i:
        if(sys.argv[i] == '--noDyn'):
            is_dyn_window = False
            print('no dyn')
        elif(sys.argv[i] == '--writesize'):
            collet_x_before_write = int(sys.argv[i+1])
            i+=2
            continue
        elif(sys.argv[i] == '--pushevery'):
            push_every_x = int(sys.argv[i+1])
            i+=2
            continue
        elif(sys.argv[i] == '--asymetrical'):
            is_asymetrical = True
        elif(sys.argv[i] == '--continueFromOld'):
            continueFromOld = True
        else:
            raise ValueError(messageParameters)
        i += 1

    # Just try to find all occurence, if doesn't exist, than it is no problem => reduces human errorrate
    vocab = TaggedVocabulary(includeWords_wo_Tags = True,with_tag_rep = True,fullOccurence=True)#The vocabulary has already been determined
    
    vocab.load(sys.argv[1])

    dir_list = os.listdir(path)
    print(dir_list)
    if continueFromOld:
        print("continue old")
        new_Dirlist = []
        for directory_name in dir_list:
            path_coocurrence = output_folder+'/'+directory_name + '.co'
            if os.path.exists(path_coocurrence):
                pass
            else:
                new_Dirlist.append(directory_name)
            dir_list = new_Dirlist

    print(dir_list)

    for directory_name in dir_list:
        file_list = os.listdir(path + '/' + directory_name)
        for file_name in file_list:
            q_files.put(path + '/'+directory_name+'/'+file_name)

    for i in range(num_processes):
        q_files.put('done')

    process_list = []
    for process_id in range(num_processes):
            p = Process(target=worker, args=(push_every_x,q_files,q_co_oc,vocab,window_size,num_processes,is_dyn_window,is_asymetrical))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))
    
    
    index = 0
    write_every = 100
    finished_processes = 0
    file_index = 0

    co_occurence = {}
    last_files_left = -1

    while finished_processes < num_processes:
        tmp = q_files.qsize()
        if tmp < last_files_left:
            print("files left" + tmp)
            last_files_left = tmp

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

        index += push_every_x

        if index >= write_every or finished_processes == num_processes:
            print('writing')
            save_coocurrences(co_occurence,output_folder + '/' + 'co-oc-dict-' + str(file_index))
            co_occurence = {}
            file_index += 1
            index = 0


    
    print('finalising')
    for process in process_list:
        process.join()


