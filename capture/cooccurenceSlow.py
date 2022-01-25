import math
import numpy as np

import os
import sys
import multiprocessing
from multiprocessing import Process, Queue
from math import *

from co_occurence import Co_Occurence_Capturer
sys.path.append("..")
from Vocabulary import *

import re
def preprocess_line(text):
    text = re.sub(r'[\'\",?!\.]',"",text)
    return text



def process_dir(dir_list,path,vocab,window_size,output_folder):
    print("hello")
    for directory_name in dir_list:
        capturer = Co_Occurence_Capturer()
        print("cap init")
        for file_name in os.listdir(path + "/" + directory_name):
            file_path = path + '/'+directory_name+'/'+file_name
            print(file_name)
            with open(file_path,'r',encoding='utf8') as in_file:
                in_lines = in_file.readlines()
                print("inlines"+str(len(in_lines)))
                for line in in_lines:
                    if line.startswith('<doc') or '</doc' in line:
                        pass
                    else:
                        line = preprocess_line(line)
                        capturer.capture(vocab,line.split(),window_size)
        capturer.save_coocurrences(output_folder+'/'+directory_name + '.co')


if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 6:
        raise ValueError('Please provide vocab , wiki-path and window_size and number of processes and output folder and [--taggedVocab]')
    pqueue = Queue()
    path = sys.argv[2]

    dir_list = os.listdir(path)
    #number = -1
    #for i in range(len(dir_list)):
    #    if dir_list[i] == 'AH':
    #        number = i
    #dir_list = dir_list[number:]
    
    window_size = int(sys.argv[3])
    num_processes = int(sys.argv[4])
    output_folder = sys.argv[5]

    is_tagged = False
    if len(sys.argv) > 6:
        if (sys.argv[6] == '--taggedVocab'):
            is_tagged = True
        else:
            raise ValueError('Please provide vocab , wiki-path and window_size and number of processes and output folder and [--taggedVocab]')
    
    if is_tagged:
        vocab = TaggedVocabulary()
    else:
        vocab = Vocabulary()
    vocab.load(sys.argv[1])
    
    dir_list = os.listdir(path)

    splitted_dirs = []
    for process in range(num_processes):
        splitted_dirs.append([])
    for dir_index in range(len(dir_list)):
        dir = dir_list[dir_index]
        splitted_dirs[dir_index % num_processes].append(dir)
    
    #delete this later
    for i in range(len(splitted_dirs)):
        print(len(splitted_dirs[i]))


    process_list = []
    for process_id in range(num_processes):
            p = Process(target=process_dir, args=(splitted_dirs[process_id],path,vocab,window_size,output_folder))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))
    
    for process in process_list:
        process.join()