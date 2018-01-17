class DataSet(object):

    @abstractmethod
    def load_data(self):
        return

    @abstractmethod
    def transform_data(self):
        """
        Converts data from raw form to a state that the model can train on.
        """
        return

class ModelArchitecture(object):
"""
Associate a DataSet object for training

have methods to initialize all objects

load weights for all the objects
(weights could be in files, or be serialized entries 
 in a database)
 Should be more specific subclasses to handle both cases.
"""
