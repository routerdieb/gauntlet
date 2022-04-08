import tensorflow as tf
import os
import numpy as np

def load_embedding(path,embedding_name):
    id_dict = {}
    word_dict = {}
    matrix = []

    full_path = os.path.join(path,embedding_name)
    #AutoDetect dims
    with open(full_path, 'r' , encoding="utf-8")  as file:
        line0 = file.readline()
        dimensions = len(line0.split())-1
    print("dimensions "+str(dimensions))
   
    with open(full_path, 'r' , encoding="utf-8")  as f:
        lines = f.readlines()
        vocab_size = len(lines)
    
        matrix = np.zeros((vocab_size,dimensions),dtype=float)
        for line in lines:
            entry = line.split()
            word = entry[0].strip()
            values = entry[1:]
            id = len(id_dict)
            id_dict[word]=id
            word_dict[id] = word
            vector = np.asarray(values, "double")
            matrix[id_dict[word],:] = vector
    print(len(id_dict))

    matrix_normalized = tf.nn.l2_normalize(matrix,axis = 1)# only use normalised version !!!
    return (word_dict,id_dict, matrix_normalized)