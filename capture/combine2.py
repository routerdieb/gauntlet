"""
Created on Mon Oct 18 22:53:19 2021

@author: weso
"""

import math
import os
import sys
import cloudpickle
sys.path.append("..//")

from Vocabulary import Vocabulary
from datetime import date

def load_co_occurence(name):
        print("combine2:"+name)
        with open(name, 'rb+') as file:
            co_occurences = cloudpickle.load(file)
        return co_occurences
    
def save_dict(path,dictionary,i,j):
    filepath = path + '//blockcounts_{ni}_{nj}'.format(ni=i,nj=j)
    with open(filepath, 'a+') as file:
        for k, v in dictionary.items():
            file.write("{k}:{v} \n".format(k=k,v=v))
            


messageParameters = 'provide pathIn pathOut and vocab-path'

def combineAndSeperate(pathIn,pathOut,vocab):
    block_size = 20000 # must be int
    blocks_amount = math.ceil(vocab.get_size()/float(block_size))

    #init dicts
    dict_of_dicts = {}
    for i in range(blocks_amount):
        for j in range(blocks_amount):
            dict_of_dicts[(i,j)] = {}
        
    file_list = os.listdir(pathIn)
    file_list.sort()
    list_of_failed = []

    for file_name in file_list:
        try:
            co_occurences = load_co_occurence(pathIn + "//" + file_name)
            print('length of ' + file_name + ':' + str(len(co_occurences)))
        except:
            list_of_failed.append(file_name)
            continue
    
        for (x,y) in co_occurences:
            x,y = int(x), int(y)
            dict_pos_x = int(x / block_size)
            dict_pos_y = int(y / block_size)
            dict_tuple = (dict_pos_x,dict_pos_y)
            x_new = x % block_size
            y_new = y % block_size
            if (x_new,y_new) in dict_of_dicts[dict_tuple]:
                dict_of_dicts[dict_tuple][(x_new,y_new)] += co_occurences[(x,y)]
            else:
                dict_of_dicts[dict_tuple][(x_new,y_new)]  = co_occurences[(x,y)]
    
            
        for (i,j) in dict_of_dicts:
            if len(dict_of_dicts[(i,j)]) > 0:#This is untested again.
                save_dict(pathOut,dict_of_dicts[(i,j)],i,j)
                dict_of_dicts[(i,j)].clear()
        
    return list_of_failed

if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 4:
        raise ValueError(messageParameters)
    vocab_path = sys.argv[3]
    print(vocab_path)
    vocab = Vocabulary()
    vocab.load(vocab_path)
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]


    if not os.listdir(pathOut):
        print("path out is empty")
    else:
        raise Exception('the block folder should be empty  ')

    list_of_failed = combineAndSeperate(pathIn,pathOut,vocab)

    #show that this step was completed in case of a regular server re-start
    print(list_of_failed)
    f = open(pathOut+"//complete.txt", "w")
    f.write("This task was completed @"+ str(date.today()))
    f.flush()
    f.write(str(list_of_failed))
    f.close()
    