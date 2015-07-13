import itertools
import scipy as sp
from Authenticator import Authenticator
from data_manip import partition_data

class CV(object):
    '''
    implements truncated leave-p-out CV
    '''


    def __init__(self, auth, data, pkd):
        '''
        takes a dictionary (username -> [(ngraph -> [latencies])])
        username maps to list of samples (1k keystrokes) represented
        as dictionaries.

        '''
        self.data = data

        self.k = {k:v[1] for k,v in pkd.items()}
        self.pkd = pkd
        self.p = {k:v[0] for k,v in pkd.items()}

        self.auth = auth(self.k)


    def validate(self):
        '''
        takes (username -> [(n-graph -> [latencies])])
        returns a list of results from several partitions of the data
        '''
        for partition in itertools.product(
                *[partition_data(u, self.data[u], self.p[u])
                for u in self.data.keys()]
        ):
            train = {x[0]:x[1] for x in list(partition)}
            val = {x[0]:x[2] for x in list(partition)}

            for inner_part in itertools.product(
                    *[partition_data(u, train[u], self.k[u])
                      for u in self.data.keys()]
            ):
                print 'fuck'


            '''

            self.auth.train(train)
            yield self.auth.evaluate(train), self.auth.evaluate(val)
            '''
