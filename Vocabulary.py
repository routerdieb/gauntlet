import json
import re
import numpy as np

class Vocabulary:
    word_frequency={}
    id2Word = []
    word2Id = {}
    block_length = 0;
    areIdsCaculated = False;
    
    def __init__(self):
        self.word_frequency={}
        self.id2Word = []
        self.word2Id = {}
    
    def setBlock_parms(self, block_length):
        self.block_length = block_length

    def build_from_text(self,text):
        for word in text:
            word = word.lower()
            try:
                self.word_frequency[word]+=1
            except KeyError:
                self.word_frequency[word]=1
    
    def save(self,filename):
        with open(filename, 'w+') as json_file:
            if(self.areIdsCaculated):
                dicted = {'word2Id':self.word2Id,'id2Word':self.id2Word}
            else:
                dicted = {'word_frequency':self.word_frequency}
            json.dump(dicted, json_file)
    
    
    def load(self,filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            try:
                self.word2Id = data['word2Id']
                self.id2Word = data['id2Word']
                self.areIdsCaculated = True
            except:
                self.word_frequency = data['word_frequency']
                self.areIdsCaculated = False
        
    def filterWord(self,word):
        self.word_frequency = {k:v for k,v in self.word_frequency.items() if word != k}

    def filter(self,number):
        self.word_frequency = dict(filter(lambda y: y[1] >= number,self.word_frequency.items()))

    def filter_just_symbol_tokens(self):
        self.word_frequency = dict(filter(lambda y: re.search(r'[a-zA-Z0-9]{1,}',y[0])!= None,self.word_frequency.items()))        
    
    def assignIds(self,shuffle=True):
        i = 0 
        for k in self.word_frequency.keys():
            self.id2Word.append(k)
        
        if shuffle:
            np.random.shuffle(self.id2Word)

        for idx in range(len(self.id2Word)):
            word = self.id2Word[idx]
            self.word2Id.update({word:idx})

        self.areIdsCaculated = True
        self.word_frequency = {}
        
    def get_size(self):
        if(self.areIdsCaculated):
            return len(self.id2Word)
        else:
            return len(self.word_frequency)
        
    def get_ids_text(self,word):
        word = word.lower()
        try:
            word_id = self.word2Id[word]
            return [word_id]
        except KeyError:
            pass
        return []


    def get_contrained_ids_text(self,word,segment):
        word = word.lower()
        try:
            word_id = self.word2Id[word]
            if(segment*self.block_length <= word_id < (segment+1)*self.block_length):
                return [word_id]
        except KeyError:
            pass
        return []


    def add_word(self,word):
        if self.areIdsCaculated:
            number = len(self.word2Id)
            self.word2Id[word] = number
            self.id2Word.append(word)
        else:
            raise Error
    
class TaggedVocabulary(Vocabulary):
    def __init__(self,wordsWithoutTags = False):
        super(TaggedVocabulary, self).__init__()
        self.wordsWithoutTags = wordsWithoutTags


    def build_from_text(self,text):
        for word in text:
            word = word.lower()
            if(not self.wordsWithoutTags):
                try:
                    self.word_frequency[word]+=1
                except KeyError:
                    self.word_frequency[word]=1
            split = word.split(chr(4))

            if(self.wordsWithoutTags):
                try:
                    self.word_frequency[split[0]]+=1
                except KeyError:
                    self.word_frequency[split[0]]=1

            if len(split) == 1:
                continue
            tag = split[1]
            if(tag == ''):
                continue
            tag = chr(4)+tag
            try:
                self.word_frequency[tag]+=1
            except KeyError:
                self.word_frequency[tag]=1




    def filter_just_symbol_tokens(self):
        self.word_frequency = {k:v for k,v in self.word_frequency.items() if k.startswith(chr(4)) or  re.search('[a-zA-Z0-9]', k)!= None }

    def get_contrained_ids_text(self,token,segment):
        token = token.lower()
        eof = chr(4)
        id_list = []
        #text (or tokenised text)
        try:
            token_id = self.word2Id[token]
            if(segment*self.block_length <= token_id < (segment+1)*self.block_length):
                id_list.append(token_id)
        except KeyError:
            pass
        #text + pos
        try:
            split = token.split(chr(4))
            if len(split) == 1:
                raise KeyError()
            tag = split[1]
            if(tag == ''):
                raise KeyError()
            tag = chr(4)+tag
            tag_id = self.word2Id[tag]
            if(segment*self.block_length <= tag_id < (segment+1)*self.block_length):
                id_list.append(tag_id)
        except KeyError:
            pass
        return id_list

    def get_ids_text(self,token):
        token = token.lower()
        eof = chr(4)
        id_list = []
        #text (or tokenised text)
        try:
            token_id = self.word2Id[token]
            id_list.append(token_id)
        except KeyError:
            pass
        #text + pos
        try:
            split = token.split(chr(4))
            if len(split) == 1:
                raise KeyError()
            tag = split[1]
            if(tag == ''):
                raise KeyError()
            tag = chr(4)+tag
            tag_id = self.word2Id[tag]
            id_list.append(tag_id)
        except KeyError:
            pass
        return id_list