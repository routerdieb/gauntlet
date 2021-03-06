import time
import math
import numpy as np
import h5py
import os
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  
import sys
sys.path.append("..")
import tensorflow as tf
from Vocabulary import *
import time
import csv
from csv_writer import *
import random

from AllMemory import *

def save_wc_emb(output_path,vocab,epochs,experiment_name):
    w, c = [None] * len(trainer.tf_weights), [None] * len(trainer.tf_con_weights)
    for i in range(len(trainer.tf_weights)):
        w[i] = trainer.tf_weights[i].numpy()
        c[i] = trainer.tf_con_bias[i].numpy()

    weights = np.concatenate(w,axis=1)
    context_weights = np.concatenate(c,axis=0)

    print(weights.shape)
    matrix = weights + np.transpose(context_weights)
    with open(output_path+'/'+experiment_name+'_'+str(epochs)+'_wc','w+',encoding='utf8') as file:
        for index,word in enumerate(vocab.id2Word):
            file.write(word)
            vector = matrix[:,index]
            for coord in vector:
                file.write(' '+str(coord))
            file.write('\n')

def save_w_emb(output_path,vocab,epochs,experiment_name):
    w, c = [None] * len(trainer.tf_weights), [None] * len(trainer.tf_con_weights)
    for i in range(len(trainer.tf_weights)):
        w[i] = trainer.tf_weights[i].numpy()
        c[i] = trainer.tf_con_bias[i].numpy()

    weights = np.concatenate(w,axis=1)
    context_weights = np.concatenate(c,axis=0)

    print(weights.shape)
    matrix = weights + np.transpose(context_weights)
    with open(output_path+'/'+experiment_name+'_'+str(epochs)+'w','w+',encoding='utf8') as file:
        for index,word in enumerate(vocab.id2Word):
            file.write(word)
            vector = matrix[:,index]
            for coord in vector:
                file.write(' '+str(coord))
            file.write('\n')



parameterMessage = 'Please provide vocab,hdf-path,output-path and experiment name and epochs --lr x.y --dims AAA'
if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 1+5:
        raise ValueError(parameterMessage)

    vocab = Vocabulary()
    vocab.load(sys.argv[1])
    size = vocab.get_size()


    path_in = sys.argv[2]
    path_out = sys.argv[3]

    experiment_name = sys.argv[4]
    epochs = int(sys.argv[5])

    if len(sys.argv) > 6:
        if(sys.argv[6] == '--lr'):
            lr = float(sys.argv[7])
        else:
            raise ValueError(parameterMessage)
    if len(sys.argv) > 8:
        if(sys.argv[8] == '--dims'):
            dim = int(sys.argv[9])
        else:
            raise ValueError(parameterMessage)

    tf.keras.backend.clear_session()
    trainer = AllMemoryTrainer(size,path_in,vector_size=dim,lr=lr)
    trainer.prepare(path_out,experiment_name+'_'+str(epochs)+"_epochs")

    startTime = time.time()

    trainer.train_splitted(epochs)

    executionTime = (time.time() - startTime)
    save_wc_emb(path_out,vocab,epochs,experiment_name)
    save_w_emb(path_out,vocab,epochs,experiment_name)
    print('Execution time in seconds: ' + str(executionTime))

    trainer.close_files()

