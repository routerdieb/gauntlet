import cloudpickle
from scipy.sparse import lil_matrix,dok_matrix
from scipy.sparse import tril
import scipy
import re
import time
import re
import os
import h5py
import numpy as np
import os
import sys
from multiprocessing import Process, Queue

# It is possible, that blocks diviside by 16 have a Performance Gain => TensorCore Utilization. E.g. 4000x4000 => --splitLengthBy 5.
# The default blocks have size of 20000, the blocks must be divisible by splitlength 
messageParameters = 'Please provide path_in path_out [--splitLengthBy X] [--processes XY]'

def load_dict(path,zeilen,spalten):
    if(zeilen >= spalten):
        template = "\\blockcounts_{i}_{j}".format(i=zeilen,j=spalten)
    else:
        template = "\\blockcounts_{i}_{j}".format(i=spalten,j=zeilen)

    file_path = path + '/' + template
    co_occurences = {}
    
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            match = re.match('\(([0-9]{1,}), ([0-9]{1,})\):([0-9.]{1,})',line)
            x = int(match.group(1))
            y = int(match.group(2))
            count = float(match.group(3))
            if (x,y) in co_occurences:
                co_occurences[(x,y)] += count
            else:
                co_occurences[(x,y)] = count
    
    return co_occurences


def load_co_occurence(path,zeilen,spalten):
    co_occurences_dict = load_dict(path,zeilen,spalten)
    print(len(co_occurences_dict))
    coocurrence = dok_matrix((20000,20000),dtype='d')
    
    coocurrence._update(co_occurences_dict)
    
    return coocurrence

def process_block(q_files,input_folder,output_folder,size,split_length):
    regex = r'blockcounts_([0-9]{1,})_([0-9]{1,})'
    while True: 
        task = q_files.get()
        if task == 'done':
            break
        else:
            file_name = task
            match = re.search(regex, file_name)
            i,j   = match.group(1), match.group(2)
            i,j   = int(i)        , int(j)
            print('output for progress ' + str(i)+','+str(j) + ':'+str(q_files.qsize()))

        co_occurence = load_co_occurence(input_folder,i,j)
        co_occurence = co_occurence.toarray()
        if(i == j):
            np.fill_diagonal(co_occurence,0)
    
        for sub_i in range(split_length):
            for sub_j in range(split_length):
                a,b = i*split_length+sub_i , j*split_length+sub_j
                #print(a,b)
                filename = 'tf_cooccurence_{a}_{b}.hdf'.format(a = a,b = b)
            
                f = h5py.File( output_folder + '/'+filename, "w")#plus experiment name
                co_occurence_hdf = f.create_dataset("co-ocurrence", (size, size))
                part = co_occurence[sub_i*size:(sub_i+1)*size,sub_j*size:(sub_j+1)*size]
                co_occurence_hdf[:,:] = part
                f.close()

if __name__ == '__main__':
    if (len(sys.argv) < 3):
        raise ValueError(messageParameters)
    print('starting dict2HDF')
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    num_processes = 4

    split_length = 4 #2,4,5,10 A value of 5 is recommeded => (block length divisable through 16) Tensor Cores
    i = 3
    while (len(sys.argv) > i):
        if(sys.argv[i] == '--splitLengthBy'):
            split_length = int(sys.argv[i+1])
            i += 2
            continue
        elif (sys.argv[i] == '--processes'):
            num_processes = int(sys.argv[i+1])
            i += 2
            continue
        else:
            raise ValueError(messageParameters)
    
    if(20000 % split_length != 0):
        raise ValueError('block not devisible by splitlengthby')
    size = int(20000/split_length)

    q_files  = Queue()
    for file_name in os.listdir(input_folder):
        q_files.put(file_name)
    
    for process in range(num_processes):
        q_files.put('done')

    process_list = []

    for process_id in range(num_processes):
            p = Process(target=process_block, args=(q_files,input_folder,output_folder,size,split_length))
            p.start()
            process_list.append(p)
            print('started #' + str(process_id))
    
    print('last phase')
    for process in process_list:
        process.join()
    print('done')


    
            