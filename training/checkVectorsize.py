import os
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError('please provide an embedding file')
    file_name = sys.argv[1]
    with open(file_name,'r',encoding='utf8') as file:
        lines = file.readlines()
        num_entrys = len(lines[0].split())-1
        print('dimensions' + str(num_entrys))