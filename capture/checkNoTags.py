import sys
sys.path.append('../')
from Vocabulary import *
import os

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError('Please provide vocab, file-in folder')
    vocab = Vocabulary()
    vocab.load(sys.argv[1])
    folder_in =  sys.argv[2]

    filtered = []
    for word in vocab.word2Id:
        if word.startswith(chr(4)):
            filtered.append(word)
            print(word)

    for file_name in os.listdir(folder_in):
        print(file_name)
        with open(folder_in + '/' +file_name,'r') as file_in:
            lines = file_in.readlines()
            for line in lines:
                match = re.match('\(([0-9]{1,}), ([0-9]{1,})\):([0-9.]{1,})',line)
                x = int(match.group(1))
                y = int(match.group(2))
                count = float(match.group(3))
                if x in filtered or y in filtered:
                    raise Exception("Found a tag")
                else:
                    pass
                    #file_out.write(line)
                    #file_out.write('\n')