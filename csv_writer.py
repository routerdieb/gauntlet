import csv

class CSV_writer:
    def __init__(self,path,name,appendmode = False):
        if (appendmode):
            self.csvfile = open(path+'/{name}'.format(name=name), 'a', newline='') 
        else:
            self.csvfile = open(path+'/{name}'.format(name=name), 'w', newline='') 
        fieldnames = ['Optimizer', 'learning_rate','epoch','loss']
        self.writer = csv.DictWriter(self.csvfile, fieldnames=fieldnames)
        self.writer.writeheader()
    
    def write(self,opt,learning_rate,epoch,loss):
        self.writer.writerow({'Optimizer': opt, 'learning_rate': learning_rate,'epoch':epoch,'loss':loss})
        self.csvfile.flush()
    
    def close(self):
        self.csvfile.close()