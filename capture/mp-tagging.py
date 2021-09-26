import sys
sys.path.append("..")
import os

import spacy
from multiprocessing import Process
import math
from time import sleep

def process_file(folder,file):
    nlp = spacy.load("en_core_web_sm")
    if not os.path.exists("S:\\lem_data\\"+folder):
        os.makedirs("S:\\lem_data\\"+folder)
    if not os.path.exists("S:\\pos_data\\"+folder):
        os.makedirs('S:\\pos_data\\'+folder)
    if not os.path.exists("S:\\ner_data\\"+folder):
        os.makedirs('S:\\ner_data\\'+folder)
                
    path = 'S:\\data\\'+folder+'\\'+file
    pos_path = 'S:\\pos_data\\'+folder+'\\'+file
    ner_path = 'S:\\ner_data\\'+folder+'\\'+file
    lemmatised_path = 'S:\\lem_data\\'+folder+'\\'+file
        
    with open(path,'r',encoding='utf8') as in_file, open(pos_path,'w',encoding='utf8') as pos_file, \
    open(ner_path,'w',encoding='utf8') as ner_file, open(lemmatised_path,'w',encoding='utf8') as lem_file:
        in_lines = in_file.readlines()
        for line in in_lines:
            if line.startswith('<doc'):
                pos_file.write(line)
                ner_file.write(line)
                lem_file.write(line)
            elif line.startswith('</doc'):
                pos_file.write(line)
                ner_file.write(line)
                lem_file.write(line)
            else:
                doc = nlp(line)
                for token in doc:
                    ner_file.write(token.text + chr(4) + token.ent_type_ + " ")
                    pos_file.write(token.text + chr(4) + token.pos_ + " ")
                    lem_file.write(token.text + chr(4) + token.lemma_ + " ")
            
                
def process_dir(path,directorys):
    print('process running')
    for directory_name in directorys:
        for file_name in os.listdir(path + "/" + directory_name):
            process_file(directory_name,file_name)
    
if __name__ == '__main__':
    number = 0
    path = 'S:\data'
    dir_list = os.listdir(path)
    
    for i in range(len(dir_list)):
        if dir_list[i] == 'CM':
            number = i
    
    for i in range(number):
        dir_list.pop(0)

    print(dir_list)
    num_processes = 12
    iterations = math.ceil(len(dir_list) / num_processes)
    for iteration in range(iterations):
        process_list = []
        for process_id in range(num_processes):
            offset = num_processes * iteration
            if(offset + process_id < len(dir_list)):
                print(dir_list[offset + process_id])
                p = Process(target=process_dir, args=(path,[dir_list[offset + process_id]],))
                p.start()
                process_list.append(p)
                print('started #' + str(process_id))
                sleep(1)
        for p in process_list:
            p.join()
        


    