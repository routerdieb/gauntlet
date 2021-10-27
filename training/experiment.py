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

def save_wc_emb(vocab,epochs):
    weights = trainer.f.get('weights')
    weights = weights[:]
    context_weights = trainer.f.get('context-weights')
    context_weights = context_weights[:]

    print(weights.shape)
    matrix = weights + np.transpose(context_weights)
    with open('..//embeddings//'+experiment_name+'_'+epochs+'_wc','w+',encoding='utf8') as file:
        for index,word in enumerate(vocab.id2Word):
            file.write(word)
            vector = matrix[:,index]
            for coord in vector:
                file.write(' '+str(coord))
            file.write('\n')

def save_w_emb(vocab,epochs):
    weights = trainer.f.get('weights')
    weights = weights[:]
    context_weights = trainer.f.get('context-weights')
    context_weights = context_weights[:]

    print(weights.shape)
    matrix = weights + np.transpose(context_weights)
    with open('..//embeddings//'+experiment_name+'_'+epochs+'w','w+',encoding='utf8') as file:
        for index,word in enumerate(vocab.id2Word):
            file.write(word)
            vector = matrix[:,index]
            for coord in vector:
                file.write(' '+str(coord))
            file.write('\n')



parameterMessage = 'Please provide vocab,hdf-path,output-path and experiment name and epochs'
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

    tf.keras.backend.clear_session()
    trainer = AllMemoryTrainer(size,"E:\\tmp\\hdf_m",vector_size=200)
    trainer.prepare(path_out,experiment_name+'_'+str(epochs)+"_epochs")

    startTime = time.time()

    trainer.train_splitted(epochs)

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))

    trainer._close_files()

