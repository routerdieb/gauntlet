import sys
sys.path.append("..")
import os

import spacy
from multiprocessing import Process
import math
from time import sleep
import re


def process_file(pathIn,pathOut,folder,file):
    nlp = spacy.load("en_core_web_sm")

    if not os.path.exists(pathOut +"lem_data/"+folder):
        os.makedirs(pathOut +"lem_data/"+folder)

    if not os.path.exists(pathOut +"pos_data/"+folder):
        os.makedirs(pathOut +"pos_data/"+folder)

    if not os.path.exists(pathOut +"ner_data/"+folder):
        os.makedirs(pathOut +"ner_data/"+folder)

    if not os.path.exists(pathOut +"tokenised_data/"+folder):
        os.makedirs(pathOut +"tokenised_data/"+folder)
                
    path            = pathIn                      + folder +'/'+ file
    pos_path        = pathOut + 'pos_data/'      + folder +'/'+ file
    ner_path        = pathOut + 'ner_data/'      + folder +'/'+ file
    lemmatised_path = pathOut + 'lem_data/'      + folder +'/'+ file
    tokenised_path  = pathOut + 'tokenised_data/'+ folder +'/'+ file
        
    with open(path,'r',encoding='utf8') as in_file, open(pos_path,'w',encoding='utf8') as pos_file, \
    open(ner_path,'w',encoding='utf8') as ner_file, open(lemmatised_path,'w',encoding='utf8') as lem_file, \
    open(tokenised_path,'w',encoding='utf8') as tok_file:
        in_lines = in_file.readlines()
        for line in in_lines:
            if line.startswith('<doc'):
                pos_file.write(line)
                ner_file.write(line)
                lem_file.write(line)
                tok_file.write(line)
            elif line.startswith('</doc'):
                pos_file.write(line)
                ner_file.write(line)
                lem_file.write(line)
                tok_file.write(line)
            else:
                line = re.sub("[ ]+"," ",line)
                doc = nlp(line)
                for token in doc:
                    ner_file.write(token.text + chr(4) + token.ent_type_ + " ")
                    pos_file.write(token.text + chr(4) + token.pos_ + " ")
                    lem_file.write(token.text + chr(4) + token.lemma_ + " ")
                    tok_file.write(token.text + " ")
            
                
def process_dir(path,directorys):
    print('process running')
    for directory_name in directorys:
        for file_name in os.listdir(path + "/" + directory_name):
            process_file(directory_name,file_name)
    
if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise ValueError('Please provide preprocessed wikipath and out path and number of processes')
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    dir_list = os.listdir(pathIn)

    print(dir_list)
    num_processes = int(sys.argv[3])
    iterations = math.ceil(len(dir_list) / num_processes)

    for iteration in range(iterations):
        process_list = []
        for process_id in range(num_processes):
            offset = num_processes * iteration
            if(offset + process_id < len(dir_list)):
                print(dir_list[offset + process_id])
                p = Process(target=process_dir, args=(pathIn,pathOut,pathIn,[dir_list[offset + process_id]],))
                p.start()
                process_list.append(p)
                print('started #' + str(process_id))
                sleep(1)
        for p in process_list:
            p.join()
        


    