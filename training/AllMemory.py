import numpy as np
import h5py
import tensorflow as tf
import Base_ModelTrainer

class AllMemoryTrainer(Base_ModelTrainer):
    blocks = {}

    def prepare(self,basepath,experiment_name,symmetrie=True):
        super.prepare(basepath,experiment_name)
        for i in range(self.amount_split):
            for j in range(self.amount_split):
                if symmetrie and j > i:
                    continue
                self.blocks[(i,j)] = self._inital_load(self,i,j)

    #conversion, pushes this already to gpu storage.

    def load_block(self,zeile,spalte):
        coocurrence = self.blocks[(zeile,spalte)]
        if (spalte > zeile):
            coocurrence = np.transpose(coocurrence)
        self.tf_co_occurences = tf.convert_to_tensor(coocurrence,dtype=tf.dtypes.float32)

    def _inital_load(self,zeile,spalte):
        file_path =  self.block_file_path(zeile,spalte)
        tmp_hf = h5py.File(file_path, "r")
        coocurrence = tmp_hf.get("co-ocurrence")[:]
        return coocurrence