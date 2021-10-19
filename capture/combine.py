# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 22:53:19 2021

@author: weso
"""

import math
import os
import sys
import cloudpickle
sys.path.append("..//")

from Vocabulary import *

def load_co_occurence(name):
        with open(name, 'rb+') as file:
            co_occurences = cloudpickle.load(file)
        return co_occurences
    
def save_dict(path,dictionary,i,j):
    filepath = path + '\\blockcounts_{ni}_{nj}'.format(ni=i,nj=j)
    with open(filepath, 'a+') as file:
        for k, v in dictionary.items():
            file.write("{k}:{v} \n".format(k=k,v=v))
            
pathIn = 'E:\\tmp\\base_dicts_nodyn'
pathOut = 'E:\\tmp\\coocurrence_blocks_nodyn'

vocab = Vocabulary()
vocab.load('../vocabs/c_base')
size = vocab.get_size()


if not os.listdir(pathOut):
    print("path out is empty")
else:
     raise Exception('the block folder should be empty  ')

def combineAndSeperate(symmetrie=True):
    block_size = 20000 # must be int
    blocks_amount = math.ceil(vocab.get_size()/float(block_size))

    #init dicts
    dict_of_dicts = {}
    for i in range(blocks_amount):
        for j in range(blocks_amount):
            dict_of_dicts[(i,j)] = {}
        
    file_list = os.listdir(pathIn)
    for file_index,file_name in enumerate(file_list):
        co_occurences = load_co_occurence(pathIn + "//" + file_name)
        print('length of ' + file_name + ':' + str(len(co_occurences)))
    
        count_removed = 0
        for (x,y) in co_occurences:
            if symmetrie and x < y:#co occurence is symetrical, zeilen präferiert => für asymetrisches feature
                count_removed += 1
                continue
            dict_pos_x = int(x / block_size)
            dict_pos_y = int(y / block_size)
            position_tuple = (dict_pos_x,dict_pos_y)
            x_new = x % block_size
            y_new = y % block_size
            if (x_new,y_new) in dict_of_dicts[position_tuple]:
                dict_of_dicts[position_tuple][(x_new,y_new)] += co_occurences[(x,y)]
            else:
                dict_of_dicts[position_tuple][(x_new,y_new)]  = co_occurences[(x,y)]
        print('removed for symetrie' + str(count_removed))
        co_occurences.clear()
        del co_occurences
            
        for (i,j) in dict_of_dicts:
            if len(dict_of_dicts[(i,j)]) > 0:#This is untested again.
                print('saving {i},{j}'.format(i=i,j=j))
                print(len(dict_of_dicts[(i,j)]))
                save_dict(pathOut,dict_of_dicts[(i,j)],i,j)
                dict_of_dicts[(i,j)].clear()
            
combineAndSeperate()