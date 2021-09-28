import math
import json
import cloudpickle

import math
class Co_Occurence_Capturer:

    def __init__(self):
        self.co_occurences = {}
        
    def _assign_entrys(self,word_ids,context_ids,dist):
        for word_id in word_ids:
                for context_id in context_ids:
                    tuple = (word_id,context_id)
                    if tuple in self.co_occurences:
                        self.co_occurences[tuple] += 1.0 / dist
                    else:
                        self.co_occurences[tuple] = 1.0 / dist


    # Window lenght is one sided length
    # The window is applied on the left and the right.
    # A window size of 0 means, just the focus_word.
    def capture_co_occurences(self,text, vocab, window_length,block_length):
        amount_split = math.ceil(vocab.get_size() / float(block_length))
        vocab.setBlock_parms(block_length)
    
        for x in range(amount_split):
            for y in range(amount_split):
                
                context_ids = []
                for focus_index,focus_word in enumerate(text):
                     left_border_of_window = max(0,focus_index - window_length)

                    window = text[left_border_of_window:focus_index+window_length+1]
                    
                                        
                   

                    focus_ids = vocab.get_contrained_ids_text(focus_word,x)
                    for c_index_window, context_word in enumerate(window):
                        c_index_text = c_index_window + left_border_of_window
                        dist = abs(c_index_text - focus_index)#Keine Ahnung ob das so richtig ist

                        context_ids = vocab.get_contrained_ids_text(context_word,y)
                        if (focus_index != c_index_text):
                            self._assign_entrys(focus_ids,context_ids,dist)                    
        return self.co_occurences
    
    def save_coocurrences(self,file_name):
        with open(file_name, 'wb') as file:
            cloudpickle.dump(self.co_occurences, file)
        self.co_occurences = {}

    def load_co_occurence(self,name):
        with open(name, 'rb+') as file:
            self.co_occurences = cloudpickle.load(file)