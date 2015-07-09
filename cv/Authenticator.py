from abc import ABCMeta, abstractmethod

class Authenticator(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def train(self, training_data):
        pass

    @abstractmethod
    def evaluate(self, val_data):
        pass


def evaluate_threshold(threshold, scores):
    '''
    takes a numerical scores threshold
    and a list of pairs of numerical scores and 1|0
    where 1 indicates a positive and 0 is a negative

    returns ipr,frr,# genuine tests, # impostor tests when marking all scores less than or equal to
    threshold as negatives
    '''
    ip,fr,gt,it = 0,0,0,0
    thresholded = [(int(threshold <= x[0]), x[1]) for x in scores]
    for i in thresholded:
        if   i[0] == 0 and i[1] == 0:
            it += 1
        elif i[0] == 0 and i[1] == 1:
            gt += 1
            fr += 1
        elif i[0] == 1 and i[1] == 0:
            it += 1
            ip += 1
        elif i[0] == 1 and i[1] == 1:
            gt += 1
    return float(ip)/it, float(fr)/gt, gt, it
