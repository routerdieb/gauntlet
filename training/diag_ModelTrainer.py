import Base_ModelTrainer
class Diag_Model(Base_ModelTrainer):
    def block_file_path(self,zeile,spalte):
        # load the hdf coocurence block
        if zeile == spalte:
            template = "tf_cooccurence_{i}_{j}_withDiag.hdf".format(i=zeile,j=spalte)
        if(zeile > spalte):
            template = "tf_cooccurence_{i}_{j}.hdf".format(i=zeile,j=spalte)
        elif(spalte > zeile):
            template = "tf_cooccurence_{i}_{j}.hdf".format(i=spalte,j=zeile)
        return  self.block_path + '\\' + template        