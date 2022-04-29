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

from Base_ModelTrainer2 import *

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



parameterMessage = 'Please provide base-vocab,vocab2,hdf-path,output-path and experiment name and epochs (or epoch1,epoch2,..) --lr x.y --dims AAA'
if __name__ == '__main__':
    print('starting')
    if len(sys.argv) < 1+5:
        raise ValueError(parameterMessage)

    base_vocab = TaggedVocabulary()
    base_vocab.load(sys.argv[1])
    base_size = base_vocab.get_size()

    vocab2 = TaggedVocabulary()
    vocab2.load(sys.argv[2])
    size2 = vocab2.get_size()


    path_in = sys.argv[3]
    path_out = sys.argv[4]

    experiment_name = sys.argv[5]
    epochs = [int(i) for i in sys.argv[6].split(",")]
    epochs.sort()
    epochs_og = epochs.copy()
    for index in range(1,len(epochs)):
        epochs[index] -= epochs_og[index-1]

    if len(sys.argv) > 7:
        if(sys.argv[7] == '--lr'):
            lr = float(sys.argv[8])
        else:
            raise ValueError(parameterMessage)
    if len(sys.argv) > 9:
        if(sys.argv[9] == '--dims'):
            dim = int(sys.argv[10])
        else:
            raise ValueError(parameterMessage)

    tf.keras.backend.clear_session()
    trainer = Dual_ModelTrainer(base_size,size2,path_in,vector_size=dim,lr=lr)
    trainer.prepare(path_out,experiment_name+'_'+str(epochs)+"_epochs")

    startTime = time.time()
    for next_training_steps,overall_epochs in zip(epochs,epochs_og):
        trainer.train_splitted(next_training_steps)
        save_w_emb(path_out,base_vocab,overall_epochs,experiment_name)

    executionTime = (time.time() - startTime)
    print('Final Execution time in seconds: ' + str(executionTime))

    trainer.close_files()

