import math
import numpy as np

import os
import sys
import multiprocessing
from multiprocessing import Process, Queue
from math import *

from co_occurenceDualVocab import Co_Occurence_DualCapturer
sys.path.append("../")
from Vocabulary import *

import re
def preprocess_line(text):
    text = re.sub(r'[\'\",?!\.]',"",text)
    text = re.sub('['+chr(4)+']sp',"",text)
    text = re.sub('['+chr(4)+']space',"",text)
    text = re.sub(r'[ ]{2,}',' ',text)
    return text



def process_dir(dir_list,path,vocab,vocab2,window_size,output_folder):
    for directory_name in dir_list:
        capturer = Co_Occurence_DualCapturer()
        for file_name in os.listdir(path + "/" + directory_name):
            file_path = path + '/'+directory_name+'/'+file_name
            print(file_name)
            with open(file_path,'r',encoding='utf8') as in_file:
                in_lines = in_file.readlines()
                for line in in_lines:
                    if line.startswith('<doc') or '</doc' in line:
                        pass
                    else:
                        line = preprocess_line(line)
                        capturer.capture(vocab,vocab2,line.split(),window_size,True)
        capturer.save_coocurrences(output_folder+'/'+directory_name + '.co')



message = 'Please provide base-vocab , tagged-vocab , wiki-path and window_size and number of processes and output folder [--continue]'


if __name__ == '__main__':
    print("This programm asummes that the first vocab is untagged and that the second one is tagged")
    print('starting')
    if len(sys.argv) < 6:
        raise ValueError(message)
    pqueue = Queue()
    path = sys.argv[3]

    window_size = int(sys.argv[4])
    num_processes = int(sys.argv[5])
    output_folder = sys.argv[6]

    dir_list = os.listdir(path)
    if (len(sys.argv) > 7 and sys.argv[7] == "--continue"):
        new_Dirlist = []
        for directory_name in dir_list:
            path_coocurrence = output_folder+'/'+directory_name + '.co'
            if os.path.exists(path_coocurrence):
                pass
            else:
                new_Dirlist.append(directory_name)
        dir_list = new_Dirlist
    
    print(dir_list)
    
    

    if len(sys.argv) > 8:
            raise ValueError(message)
    
    
    vocab = TaggedVocabulary(includeWords_wo_Tags = True)
    vocab2 = TaggedVocabulary()
    

    vocab.load(sys.argv[1])
    vocab2.load(sys.argv[2])


    splitted_dirs = []
    for process in range(num_processes):
        splitted_dirs.append([])
    for dir_index in range(len(dir_list)):
        dir = dir_list[dir_index]
        splitted_dirs[dir_index % num_processes].append(dir)
    
    for i in range(len(splitted_dirs)):
        print(len(splitted_dirs[i]))


    process_list = []
    for process_id in range(num_processes):
            p = Process(target=process_dir, args=(splitted_dirs[process_id],path,vocab,vocab2,window_size,output_folder))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))
    
    for process in process_list:
        process.join()
