from abc import ABCMeta, abstractmethod

class Authenticator(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def train(self, training_data):
        pass

    @abstractmethod
    def evaluate(self, val_data):
        pass
