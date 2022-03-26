from asyncio.windows_events import NULL
import numpy as np;
import tensorflow as tf;
import sys
#Path to flair (pip install was broken)
sys.path.append(r'C:\Users\weso\Desktop\flair')
import torch

from flair.datasets import CONLL_03
from flair.embeddings import WordEmbeddings, FlairEmbeddings, StackedEmbeddings, TokenEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.embeddings.token import WordEmbeddings
from typing import List, Union
from flair.data import DT

matrix = []
id_dict = {}
word_dict = {}
matrix_normalized = []

def loadEmbedding(path, emb_name):
    global matrix
    global matrix_normalized
    global word_dict
    global id_dict
    #AutoDetect dims
    #test with base2021_300
    with open(path + emb_name, 'r' , encoding="utf-8")  as file:
        line0 = file.readline()
        dimensions = len(line0.split())-1
    print("dimensions "+str(dimensions))
    
    with open(path + emb_name, 'r' , encoding="utf-8")  as f:
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
    matrix = []

class GauntletWordEmbeddings(TokenEmbeddings):
    

    @property
    def embedding_length(self) -> int:
        return 500

    def get_vec(self, word: str) -> torch.Tensor:
        try:
            id = id_dict[word.lower()]
            print(id)
            searched_vector = matrix_normalized[id,:]
            searched_vector = tf.transpose(searched_vector)
            print(searched_vector.shape)
            return torch.from_numpy(searched_vector.numpy())
        except KeyError:
            return torch.from_numpy(np.zeros((500)))

    name = "GauntletBaselineWordEmbedding"
    embeddings = name

    def embed(self, data_points: Union[DT, List[DT]]) -> List[DT]:
        """Add embeddings to all words in a list of sentences. If embeddings are already added, updates only if embeddings
        are non-static."""

        # if only one sentence is passed, convert to list of sentence
        if not isinstance(data_points, list):
            data_points = [data_points]
        
        print(chr(4))
        for Sentence in data_points:
            for token in Sentence:
                emb = self.get_vec(token.text)
                token.set_embedding('GauntSomeName', emb)
                print(token)
        
        print(data_points)
        return data_points

    

        


# 1. get the corpus
corpus = CONLL_03()
print(corpus)

# 2. what label do we want to predict?
label_type = 'ner'

# 3. make the label dictionary from the corpus
label_dict = corpus.make_label_dictionary(label_type=label_type)
print(label_dict)

loadEmbedding("E:/","cleanDeleteDynDict_150w")
# 4. initialize embedding stack with Flair and GloVe
embedding_types = [
    GauntletWordEmbeddings(),
]

embeddings = StackedEmbeddings(embeddings=embedding_types)

# 5. initialize sequence tagger
tagger = SequenceTagger(hidden_size=256,
                        embeddings=embeddings,
                        tag_dictionary=label_dict,
                        tag_type=label_type,
                        use_crf=True)

# 6. initialize trainer
trainer = ModelTrainer(tagger, corpus)

# 7. start training
trainer.train('resources/taggers/nerGlove-flair',
              learning_rate=0.1,
              mini_batch_size=32,
              max_epochs=150)