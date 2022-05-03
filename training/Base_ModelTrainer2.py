   
import cloudpickle
import os
import sys
sys.path.append('../')
import h5py
from Vocabulary import *
from csv_writer import *
import tensorflow as tf
import numpy as np
import random
import math
import threading
import time
from tensorflow.keras import mixed_precision
import threading, queue

class Base_ModelTrainer2:
    def __init__(self,vocab_length,block_path,vector_size,lr):
        self.vector_size = vector_size
        # AND HERE IT IS AGAIN
        self.block_length = 5000
        self.amount_split = math.ceil(vocab_length/float(self.block_length))
        print('amout_split: ' + str(self.amount_split))
        self.block_path = block_path
        self.vocab_length = vocab_length
        self.optimizer = None
        self.lr = lr
        self.ones_symetrical = tf.ones((self.block_length,self.block_length), dtype=tf.dtypes.float32, name=None)
    
    def prepare(self,basepath,experiment_name):
        self.basepath = basepath
        self.experiment_name = experiment_name
        self.f = h5py.File(basepath + '//{filename}.hdf5'.format(filename=experiment_name), "w")
        #initalize all the HDF files
        self.con_weights = self.f.create_dataset("context-weights", (self.vocab_length, self.vector_size))
        self.weights = self.f.create_dataset("weights",(self.vector_size,self.vocab_length))
        self.context_bias = self.f.create_dataset("context-bias", (self.vocab_length,1))
        self.bias = self.f.create_dataset("bias", (1,self.vocab_length))
        self.csv_writer = CSV_writer(basepath,experiment_name+".csv")

        self.init_weights()
        self._init_matrices()
        
    def _init_matrices(self,chunk_size=10000):
        self._init_hdf_matrix(self.weights,-0.5,0.5,chunk_size)
        self._init_hdf_matrix(self.con_weights,-0.5,0.5,chunk_size)
        self._init_hdf_matrix(self.context_bias,-0.5,0.5,chunk_size)
        self._init_hdf_matrix(self.bias,-0.5,0.5,chunk_size)


    def _init_hdf_matrix(self,hdf_data,min_value,max_value,block_length):
        if len(hdf_data) > len(hdf_data[0]):
            iterations = int(math.ceil(len(hdf_data) / float(block_length)))
            for i in range(iterations):
                current_size = min(block_length,len(hdf_data)-block_length*i)
                hdf_data[i*block_length:(i+1)*block_length , :] = np.random.rand(current_size,len(hdf_data[0]))/self.vector_size
        else:
            iterations = int(math.ceil(len(hdf_data[0]) / float(block_length)))
            for i in range(iterations):
                current_size = min(block_length,len(hdf_data[0])-block_length*i)
                hdf_data[:,i*block_length:(i+1)*block_length] = np.random.rand(len(hdf_data),current_size)/self.vector_size



    def resume(self,basepath,experiment_name):
        self.basepath = basepath
        self.experiment_name = experiment_name
        self.f = h5py.File(basepath + '//{filename}.hdf5'.format(filename=experiment_name), "w")
        
        self.init_weights()
        self.load_optimizer()
        self.csv_writer = CSV_writer(basepath,experiment_name+".csv",appendmode = True)

    def init_weights(self):
        iterations = math.ceil(self.vocab_length/self.block_length) 
        self.tf_weights,self.tf_con_weights,self.tf_bias, self.tf_con_bias  = \
        [None]*iterations,[None]*iterations,[None]*iterations,[None]*iterations
        
        for iter in range(iterations):
            # seems like i don't need fillage
            block_fillage = min(self.block_length, self.vocab_length - iter * self.block_length)
            
            self.tf_weights[iter]    = tf.Variable(initial_value=self.weights[:,iter * self.block_length:(iter+1)*self.block_length],dtype=tf.dtypes.float32)
            self.tf_con_weights[iter]= tf.Variable(initial_value=self.con_weights[iter * self.block_length:(iter+1)*self.block_length,:],dtype=tf.dtypes.float32)
            self.tf_bias[iter]       = tf.Variable(initial_value=self.bias[:,iter * self.block_length:(iter+1)*self.block_length],dtype=tf.dtypes.float32)
            self.tf_con_bias[iter]   = tf.Variable(initial_value=self.context_bias[iter * self.block_length:(iter+1)*self.block_length,:],dtype=tf.dtypes.float32)
        
        
    def save_weights(self):
        iterations = math.ceil(self.vocab_length/self.block_length) 
        for iter in range(iterations):
            # seems like i don't need fillage
            block_fillage = min(self.block_length, self.vocab_length - iter * self.block_length)
            
            self.weights[:,iter * self.block_length:(iter+1)*self.block_length] = self.tf_weights[iter].numpy()
            self.context_bias[iter * self.block_length:(iter+1)*self.block_length,:] = self.tf_con_bias[iter].numpy()
            self.bias[:,iter * self.block_length:(iter+1)*self.block_length] = self.tf_bias[iter].numpy()
            self.con_weights[iter * self.block_length:(iter+1)*self.block_length,:] = self.tf_con_weights[iter].numpy()
           
    def save_optimizer(self,file_path):
        with open(file_path, 'wb') as file:
            cloudpickle.dump(self.optimizer, file)

    def load_optimizer(self,file_path):
        with open(file_path, 'rb+') as file:
            self.optimizer = cloudpickle.load(file)

    def close_files(self):
        self.f.close()
        self.csv_writer.close()
            
    
    def block_file_path(self,zeile,spalte):
        # load the hdf coocurence block
        if(zeile >= spalte):
            template = "tf_cooccurence_{i}_{j}.hdf".format(i=zeile,j=spalte)
        else:
            template = "tf_cooccurence_{i}_{j}.hdf".format(i=spalte,j=zeile)
        
        return  os.path.join(self.block_path ,template)
        
    file_que = queue.Queue()
    
    
    
    
    def load_block(self,zeile,spalte):
        file_path =  self.block_file_path(zeile,spalte)
        
        
        tmp_hf = h5py.File(file_path, "r")
        coocurrence = tmp_hf.get("co-ocurrence")[:]
        if (spalte > zeile):
            coocurrence = np.transpose(coocurrence)
        self.tf_co_occurences = tf.convert_to_tensor(coocurrence,dtype=tf.dtypes.float32)
        coocurrence = None
        tmp_hf.close()
    
    
    
    def load_block_async(self,zeile,spalte):
        self.thread = threading.Thread(target=self.thread_load,args=(zeile,spalte))
        self.thread.start()

    def get_block_async(self):
        self.thread.join()
        self.tf_co_occurences = self.file_que.get()
        
    
    def thread_load(self,zeile,spalte):
        file_path =  self.block_file_path(zeile,spalte)
        
        tmp_hf = h5py.File(file_path, "r")
        coocurrence = tmp_hf.get("co-ocurrence")[:]
        if (spalte > zeile):
            coocurrence = np.transpose(coocurrence)
        tf_co_occurences = tf.convert_to_tensor(coocurrence,dtype=tf.dtypes.float32)
        coocurrence = None
        tmp_hf.close()
        
        self.file_que.put(tf_co_occurences)
        tf_co_occurences = None
        
   
    def _inner_loss(self,weights,context_weights,bias_terms,co_occurences):
        #co_occurences = tf.clip_by_value(co_occurences, clip_value_min = 0.0, clip_value_max=5000.0)
        weight_matrix = tf.matmul(context_weights,weights)
        log_X = tf.math.log(co_occurences + self.ones_symetrical)
        summe = bias_terms + weight_matrix - log_X
        summe = tf.math.square(summe)
        summe = self.scale_fn(co_occurences) * summe#elemend wise
        reduced = tf.math.reduce_sum(summe)
        return reduced

    def load(self,id, zeile, spalte,block_list):
        if(id == 0):
            self.load_block(zeile,spalte)
            self.load_block_async(block_list[id+1][0],block_list[id+1][1])
        else:
            self.get_block_async()
            if(id < len(block_list) - 1):#if not last id
                next = block_list[id+1]
                self.load_block_async(next[0],next[1])

    def loss(self,zeile,spalte,weights,context_weights,bias,con_bias,co_occurences):
    
        #just the words context
        if(zeile == self.amount_split - 1):
            difference = self.block_length - con_bias.shape[0]
            add2_context_bias   = tf.zeros((difference,1),dtype=tf.dtypes.float32)
            add2_context_weights = tf.zeros((difference,self.vector_size),dtype=tf.dtypes.float32)
            
            con_weights       = tf.concat([context_weights,add2_context_weights],axis = 0)
            con_bias   = tf.concat([con_bias,add2_context_bias],axis = 0)
        else:
            con_weights       = context_weights
        
        co_occurences = self.tf_co_occurences
        #just the words without context
        if(spalte == self.amount_split - 1):
            difference = self.block_length - bias.shape[1]
            add2_bias = tf.zeros((1,difference),dtype=tf.dtypes.float32)
            add2_weights = tf.zeros((self.vector_size,difference),dtype=tf.dtypes.float32)
            
            weights = tf.concat([weights,add2_weights],axis = 1)
            bias = tf.concat([bias,add2_bias],axis=1)
        else:
            weights     = weights
        biasMat = tf.math.multiply(bias, con_bias)
        return self._inner_loss(weights,con_weights,biasMat,co_occurences)
    
    alpha = tf.constant(0.75,dtype=tf.dtypes.float32)
    XMAX = tf.constant(100.0,dtype=tf.dtypes.float32)
    
    def scale_fn(self,value):
        clipped = tf.clip_by_value(value, clip_value_min = 0.0, clip_value_max=100.0)
        return tf.pow(clipped / self.XMAX, self.alpha)
    




    def train_splitted(self,epochs,mixedPrecision = False):

        #if optimizer is set, than this is continue training
        if (self.optimizer == None):
            self.optimizer = tf.keras.optimizers.Adagrad(learning_rate=self.lr,clipvalue=100.0)
            self.init_weights()
        if(mixedPrecision):
            policy = mixed_precision.Policy('mixed_float16')
            mixed_precision.set_global_policy(policy)
            
        for epoch in range(epochs):
            cur_loss = 0.0
            
            
            block_list = [(x,y) for x in range(self.amount_split) for y in range(self.amount_split) if x >= y]
            random.shuffle(block_list)
        
            enumerated = enumerate(block_list)
            for id,(zeile,spalte) in enumerated:
                self.load(id,zeile,spalte,block_list)
                    
                #train code
                with tf.GradientTape() as tape:
                    tmp_loss = self.loss(zeile,spalte,self.tf_weights[spalte],self.tf_con_weights[zeile],\
                    self.tf_bias[spalte],self.tf_con_bias[zeile],self.tf_co_occurences)
                    
                    weights = [self.tf_weights[spalte],self.tf_con_weights[zeile],\
                    self.tf_bias[spalte],self.tf_con_bias[zeile]]
                    grads = tape.gradient(tmp_loss, weights)
                    #grads, _ = tf.clip_by_global_norm(grads, 5.0)
                    self.optimizer.apply_gradients(zip(grads, weights))
                cur_loss += tmp_loss.numpy()
                     
                #train the other side
                if spalte != zeile:
                    self.tf_co_occurences = tf.transpose(self.tf_co_occurences)
                    
                    #train code
                    with tf.GradientTape() as tape:
                        tmp_loss = self.loss(spalte,zeile,self.tf_weights[zeile],self.tf_con_weights[spalte],\
                        self.tf_bias[zeile],self.tf_con_bias[spalte],self.tf_co_occurences)
                        
                        weights = [self.tf_weights[zeile],self.tf_con_weights[spalte],\
                        self.tf_bias[zeile],self.tf_con_bias[spalte]]
                        
                        grads = tape.gradient(tmp_loss, weights)
                        #capped_grads = [tf.clip_by_norm(grad,5.0) for grad in grads]
                    self.optimizer.apply_gradients(zip(grads, weights))
                    cur_loss += tmp_loss.numpy()
                           
            self.save_weights()    
            print('epoch: '+str(epoch)+" loss: "+str(int(cur_loss)))
            #lrOnPlato.notify_loss(cur_loss.numpy(),epoch)
            self.csv_writer.write('Adagrad',0.5,epoch+1,cur_loss)
        #self._close_files()
        return None