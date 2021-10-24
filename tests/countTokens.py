import os
path = "E:\\data2021processed\\tokenised_data\\"

count = 0
for directory in os.listdir(path):
    print(directory , count)
    for file in os.listdir(path + directory):
        with open(path + directory + '\\' +file,'r',encoding='utf8') as in_file:
            in_lines = in_file.readlines()
            for line in in_lines:
                if line.startswith('<doc') or '</doc' in line:
                    pass
                else:
                    count += len(line.split())
print(count)