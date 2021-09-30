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
                    
                    focus_ids = vocab.get_contrained_ids_text(focus_word,x)
                    
                    #left words
                    window_left = []
                    current_position = focus_index - 1
                    while(len(window_left) < window_length and current_position >= 0):
                        word = text[current_position]
                        if( word in vocab.word2Id):#is not filtered out word
                            window_left.insert(0,word)
                        current_position -= 1
                    for index,context_word in enumerate(window_left):
                        dist = abs(len(window_left) - index)
                        context_ids = vocab.get_contrained_ids_text(context_word,y)
                        self._assign_entrys(focus_ids,context_ids,dist) 
                        
                    #rigth words
                    window_right = []
                    current_position = focus_index + 1
                    while(len(window_right) < window_length and current_position < len(text)):
                        word = text[current_position]
                        if( word in vocab.word2Id):
                            window_right.append(word)
                        current_position += 1
                    
                    for index,context_word in enumerate(window_right):
                        dist = abs(1+ index)
                        context_ids = vocab.get_contrained_ids_text(context_word,y)
                        self._assign_entrys(focus_ids,context_ids,dist) 
                            
        return self.co_occurences
    
    def save_coocurrences(self,file_name):
        with open(file_name, 'wb') as file:
            cloudpickle.dump(self.co_occurences, file)
        self.co_occurences = {}

    def load_co_occurence(self,name):
        with open(name, 'rb+') as file:
            self.co_occurences = cloudpickle.load(file)