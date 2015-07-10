import collections as coll
import preprocessor as pp

from Authenticator import Authenticator
from CV import CV
from Density import DensityAuth

import data_manip

class TestAuth(Authenticator):
    def train(self, training_data):
        pass


    def evaluate(self, val_data):
        pass


if __name__=='__main__':
    """
    test_data = {'a' : [coll.defaultdict(list, {'aa' : range(10,100,10),
                                                'ab' : range(1,10)}),
                        coll.defaultdict(list, {'ac' : range(1,10,2),
                                                'aa' : [2,2,2]}),
                        coll.defaultdict(list, {'ad' : range(10, 20, 3)})
                    ],
                 'b' : [coll.defaultdict(list, {'ba' : range(1,20,3),
                                                'bb' : range(1,15)}),
                        coll.defaultdict(list, {'bc' : range(2,20,4)}),
                        coll.defaultdict(list, {'bd' : range(50,300,150)})
                    ],
    }
    """
    test_data = pp.split_samples(pp.load_data())
    for u in test_data.keys():
        if u not in {'9999999','SERLHOU'}:
            del test_data[u]
    print test_data.keys()
    test_cv = CV(DensityAuth, test_data)
    '''

    for i in test_cv.partition_data('shit', test_data['a'], 1):
        fuck.pprint(i)
    '''

    for i in test_cv.validate():
        pass
    print "DONESKI"
