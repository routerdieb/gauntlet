import sys
sys.path.append("..")
import os

import spacy
from multiprocessing import Process
import math
from time import sleep


def process_file(pathIn,pathOut,directory_name,file_name):
    nlp = spacy.load("en_core_web_sm")

    if not os.path.exists(pathOut +"/pos_treebank_data/"+directory_name):
        os.makedirs(pathOut +"/pos_treebank_data/"+directory_name)
             
    pos_treebank_path        = pathOut + '/pos_treebank_data/'      + directory_name +'/'+ file_name
    in_path = pathIn + '/'+ directory_name + "/" + file_name    
    
    with open(in_path,'r',encoding='utf8') as in_file, open(pos_treebank_path,'w',encoding='utf8') as pos_tree_file:
        in_lines = in_file.readlines()
        for line in in_lines:
            if line.startswith('<doc') or '<doc' in line[:30]:
                pos_tree_file.write(line)
            elif line.startswith('</doc') or '</doc' in line[:30]:
                pos_tree_file.write(line)
            else:
                doc = nlp(line)
                for token in doc:
                    pos_tree_file.write(token.text + chr(4) + token.tag_ + " ")
            
                
def process_dir(pathIn,pathOut,directorys):
    print('process running')
    for directory_name in directorys:
        for file_name in os.listdir(pathIn + "/" + directory_name):
            process_file(pathIn,pathOut,directory_name,file_name)
    
if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise ValueError('Please provide preprocessed wikipath and out path and num processes')
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    dir_list = os.listdir(pathIn)

    #In case it is needed to continue at some folder
    # number = 0
    #for i in range(len(dir_list)):
    #    if dir_list[i] == 'EE':
    #       number = i
    #for i in range(number):
    #    dir_list.pop(0)

    print(dir_list)
    num_processes = int(sys.argv[3])
    iterations = math.ceil(len(dir_list) / num_processes)
    for iteration in range(iterations):
        process_list = []
        for process_id in range(num_processes):
            offset = num_processes * iteration
            if(offset + process_id < len(dir_list)):
                print(dir_list[offset + process_id])
                p = Process(target=process_dir, args=(pathIn,pathOut,[dir_list[offset + process_id]],))
                p.start()
                process_list.append(p)
                print('started #' + str(process_id))
                sleep(1)
        for p in process_list:
            p.join()
        