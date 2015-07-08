import pprint

from Authenticator import Authenticator
from CV import CV
import Density as dn

class test_auth(Authenticator):
    def train(self, training_data):
        refProf = dn.density(training_data[:len(training_data)//3])
        trainingProf = dn.density(training-data[len(trainin_data)//3:])
        dn.difference(refProf,trainingProf)
    def evaluate(self, val_data):
        print 'validating', val_data
        print

if __name__=='__main__':
    test_data = {'a' : [{'aa' : range(10,1000,100),
                         'ab' : range(10)},
                        {'ac' : range(0,10,2)},
                        {'ad' : range(10, 20, 3)}
                    ],
                 'b' : [{'ba' : range(0,20,3),
                         'bb' : range(15)},
                        {'bc' : range(2,20,4),
                         'bd' : range(50,300,150)}
                    ],
    }

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
