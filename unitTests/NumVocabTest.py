import unittest
import math
import os
import sys
sys.path.append("..//")
from Vocabulary import *

class NumVocabTest(unittest.TestCase):

    NUM_TEXT = "num"
    def setUp(self):
        self.vocab = Vocabulary()

    def testContainedEndOfString(self):
        textSample = "once there was a string, which contain a NUM"
        vocab = self.vocab
        vocab.build_from_untokenised_text(textSample)
        vocab.assignIds()
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != [])
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != None)

    def testContainedFromTo(self):
        textSample = "from NUM to NUM as part of La Louisiane"
        vocab = self.vocab
        vocab.build_from_untokenised_text(textSample)
        vocab.assignIds()
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != [])
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != None)
    
    def testContainedAfterDefaultFiltering(self):
        textSample = "once there was a string, which contain a NUM ." * 100
        textSample = textSample
        vocab = self.vocab
        vocab.build_from_untokenised_text(textSample)
        vocab = self.filter(vocab)
        vocab.assignIds()
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != [])
        self.assertTrue(vocab.get_ids_text(self.NUM_TEXT) != None)
        print(vocab.get_ids_text(self.NUM_TEXT))

    def filter(self,vocab):
        vocab.filter_just_symbol_tokens()
        vocab.filter(100)
        vocab.filterWord(''+chr(4))#just the seperation symbol
        vocab.filterWord('')#The empty Word
        return vocab





if __name__ == '__main__':
    unittest.main()