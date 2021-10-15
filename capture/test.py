import math
import numpy as np

import os
import sys
sys.path.append("..")
import multiprocessing
from multiprocessing import Process, Queue
from time import sleep
import time

from Vocabulary import *

save_file = 'ner_vocab4'
global_vocabulary = TaggedVocabulary()
global_vocabulary.load('../vocabs/unfiltered' + save_file)
print(global_vocabulary.get_size())
global_vocabulary.filter_just_symbol_tokens()
print(global_vocabulary.get_size())
global_vocabulary.filter(100)
print(global_vocabulary.get_size())
global_vocabulary.filterWord(''+chr(4))
print(global_vocabulary.get_size())
global_vocabulary.assignIds()
print('global_vocabulary_post_filtering')
print(global_vocabulary.get_size())
global_vocabulary.save('../vocabs/' + save_file)