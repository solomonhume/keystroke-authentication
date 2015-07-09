import collections as coll
import pprint

from Authenticator import Authenticator
from CV import CV

import Density as dn
import data_manip
from GammaBayesFactorAuthenticator import GammaBFAuth


class TestAuth(Authenticator):
    def train(self, training_data):
        print 'training', training_data
        print 


    def evaluate(self, val_data):
        print 'validating', val_data
        print


if __name__=='__main__':

    test_data = {'a' : [coll.defaultdict(list, {'aa' : range(10,1000,100), 
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
    test_auth = GammaBFAuth
    
    test_cv = CV(test_auth, test_data)
    pp = pprint.PrettyPrinter()
    pp.pprint(test_cv.p)
    '''

    for i in test_cv.partition_data('shit', test_data['a'], 1):
        fuck.pprint(i)
    '''
    print 'test dataset:'
    pp.pprint(test_data)
    print

    for i in test_cv.validate():
        pass
