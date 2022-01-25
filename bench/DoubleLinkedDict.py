#Without Generics, this is stupid.
class bijection2int:

    def __init__(self):
        self.__current_id = 0
        self.__thing2id = {}
        self.__id2thing = {}
    
    def add(self,thing):
        self.__thing2id[thing] = self.__current_id
        self.__id2thing[self.__current_id] = thing
        self.__current_id += 1

    def getId(self,thing):
        return self.__thing2id[thing]

    def getThingById(self,id):
        return self.__id2thing[id]

    def getThings(self):
        return self.__thing2id.keys()

    def containsAll(self,iterable):
        for object in iterable:
            if object not in self.__thing2id:
                return False
        return True