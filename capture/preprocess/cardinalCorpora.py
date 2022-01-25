import sys
sys.path.append("..")
import os

from multiprocessing import Process
import math
from time import sleep
from findCardinals import *

def create_path(basepath,a,directory_name):
    return basepath +"/"+a+"/"+directory_name

def create_folders(basepath,array,directory_name):
    for a in array:
        path = create_path(basepath,a,directory_name)
        if not os.path.exists(path):
            os.makedirs(path)

def process_file(pathIn,pathOut,directory_name,file_name,isUniversalTagset):
    #create folders, for cd, num,cd_ordinal and num_ordinal
    if isUniversalTagset:
        folders = ["num","num_ordinal"]
    else:
        folders = ["cd","cd_ordinal"]
    create_folders(pathOut,folders,directory_name)

    in_path = pathIn + "/"+ directory_name+"/"+file_name;
    for fold in folders:
        outFilePath = create_path(pathOut,fold,directory_name)+'/'+file_name
        with open(in_path,'r',encoding='utf8') as in_file:
            with open(outFilePath,'w',encoding='utf8') as outFile:
                in_lines = in_file.readlines()
                for line in in_lines:
                    if line.startswith('<doc') or '<doc' in line[:30]:
                        outFile.write(line)
                    elif line.startswith('</doc') or '</doc' in line[:30]:
                        outFile.write(line)
                    else:
                        if fold in("cd","num"):
                            outFile.write(find_card(line))
                        if fold in ("cd_ordinal","num_ordinal"):
                            outFile.write(find_cardAndOrdinalClean(line))
                
def process_dir(pathIn,pathOut,isUniTagset,directorys):
    print('process running')
    for directory_name in directorys:
        for file_name in os.listdir(pathIn + "/" + directory_name):
            process_file(pathIn,pathOut,directory_name,file_name,isUniTagset)
    
if __name__ == '__main__':
    if len(sys.argv) != 5:
        raise ValueError('Please provide preprocessed wikipath and out path and num processes and isUniversalTagset (True or False)')
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    isUniversal = bool(sys.argv[4])
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
                p = Process(target=process_dir, args=(pathIn,pathOut,isUniversal,[dir_list[offset + process_id]],))
                p.start()
                process_list.append(p)
                print('started #' + str(process_id))
                sleep(1)
        for p in process_list:
            p.join()
        