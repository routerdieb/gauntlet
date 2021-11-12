import sys
sys.path.append('../')
from Vocabulary import *
import os
import re

if __name__ == '__main__':
    if len(sys.argv) < 4:
        raise ValueError('Please provide vocab, file-in folder and file-out folder')
    vocab = Vocabulary()
    vocab.load(sys.argv[1])
    folder_in =  sys.argv[2]
    folder_out =  sys.argv[3]

    filtered = []
    filtered_ids = []
    for word in vocab.word2Id:
        if word.startswith(chr(4)):
            filtered.append(word)
            print(word)
            filtered_ids.append(vocab.word2Id[word])
    print(filtered_ids)

    for file_name in os.listdir(folder_in):
        print(file_name)
        with open(folder_in + '/' +file_name,'r') as file_in, open(folder_out + '/' +file_name,'w+') as file_out:
            lines = file_in.readlines()
            for line in lines:
                match = re.match('\(([0-9]{1,}), ([0-9]{1,})\):([0-9.]{1,})',line)
                x = int(match.group(1))
                y = int(match.group(2))
                count = float(match.group(3))
                if x in filtered_ids or y in filtered_ids:
                    pass
                else:
                    file_out.write(line)
                    #file_out.write('\n')