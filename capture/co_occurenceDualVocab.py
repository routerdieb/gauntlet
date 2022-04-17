import math
import json
import cloudpickle

import math
import time
class Co_Occurence_DualCapturer:

    def __init__(self,isDyn = True):
        self.co_occurences = {}
        self.isDyn = isDyn
        
    def _assign_entrys(self,word_ids,context_ids,dist):
        #print(word_ids, "    ", context_ids)
        if not self.isDyn:
            dist = 1.0
        for word_id in word_ids:
                for context_id in context_ids:
                    tuple = (word_id,context_id)
                    if tuple in self.co_occurences:
                        self.co_occurences[tuple] += 1.0 / float(dist)
                    else:
                        self.co_occurences[tuple] = 1.0 / float(dist)


    # Window lenght is one sided length
    # The window is applied on the left and the right.
    # A window size of 0 means, just the focus_word.
    # Article tokens is of type list
    def capture(self,word_vocab,context_vocab,article_tokens,window_size):
        word_ids = []
        context_ids = []
        for token in article_tokens:
            print(token)
            cur_word_ids = word_vocab.get_ids_text(token)
            word_ids.append(cur_word_ids)
            cur_context_ids = context_vocab.get_ids_text(token)
            context_ids.append(cur_context_ids)

        print(str(cur_context_ids)[0:1000])
        print(str(word_ids)[0:1000])
        sleep(1000)

        for focus_position,focus_ids in enumerate(word_ids):
            window_left = context_ids[max(0,focus_position-window_size):focus_position]
           
            for position,ids in enumerate(window_left):
                dist = abs(len(window_left) - position)
                self._assign_entrys(focus_ids,ids,dist)
        
            window_right = context_ids[focus_position+1:focus_position+1+window_size]
            
            for position,ids in enumerate(window_right):
                dist = abs(1+ position)
                self._assign_entrys(focus_ids,ids,dist)

        print(len(self.co_occurences))
        return self.co_occurences
    
    def save_coocurrences(self,file_name):
        with open(file_name, 'wb') as file:
            cloudpickle.dump(self.co_occurences, file)
        self.co_occurences = {}

    def load_co_occurence(self,name):
        with open(name, 'rb+') as file:
            self.co_occurences = cloudpickle.load(file)