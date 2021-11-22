# pre requirements:
# already created the vocabulary
# 
from math import e
import os


def co_ocurrence():
    pass




def create_hdf_dir():
    pass


def hdf():
     python dict2Hdf.py ../../penn_tagged_woTagRep_combined/ /home/tmp/wesolekm/treebank_wo_hdfs/ --processes 30


def train():
    os.system("deactivate")
    os.system("$Home")
    os.system("source gauntlet_env/tf-venv/bin/activate")
    os.system("cd gauntlet/training/")
    #all the parameters again
    # set visibile devices to 1, as all the other people use gpu0 => avoid them
    python experiment.py ../vocabs/treebank_tagged /home/tmp/wesolekm/treebank_wo_hdfs/ /vol/tmp/wesolekm/ treebank_tagged_woTags 100 --lr 0.5 --dims 500

if __name__ == '__main__':
    print('starting')
    

    experiment_base_name = ""
    pathSteps = ""
    data_path = ""
    
    appendix = ""
    if tagrep:
        appendix += "wTagRep"
    else:
        appendix += "NoTagRep"

    expeiment_name = experiment_base_name + "_"+ str(tagRep)
    
    #mkdirs
    os.system("cd " + pathSteps)
    os.mkdir(expeiment_name + "_blob")
    os.mkdir(expeiment_name + "_combined")
    os.mkdir(expeiment_name + "_hdf")
    
    #coocurrence
    os.system("python ./mp-cooccurence.py "+vocab_path+" "+data_path+" 10 30 "+pathSteps+expeiment_name+"_blob")