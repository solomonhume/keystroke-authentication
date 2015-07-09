import collections as coll

import pylab as P
import scipy.stats as stats

from Authenticator import Authenticator
from data_manip import to_lat_dict, process_latencies

class GammaBFAuth(Authenticator):
    def __init__(self):
        self.params = {}
        

    def train(self, training_data):
        temp = to_lat_dict(training_data)
        for u in temp.keys():
            print temp[u].keys()
        self.params = process_latencies(to_lat_dict(training_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda x: (-1.,-1.,-1.)
        )
        print self.params
    

    def evaluate(self, val_data):
        pass
