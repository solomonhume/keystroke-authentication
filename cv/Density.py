import numpy as np
import statsmodels.api as sm
from scipy import stats
import itertools

from Authenticator import Authenticator
from data_manip import to_lat_dict, process_latencies
from density_auth import kdensity,difference,determineThresh,evaluateThresh


class DensityAuth(Authenticator):
    def __init__(self,kd):
        self.kd = kd
        
    def train(self,training_data):
        print len(training_data)
        data_num = xrange(len(data_num))
        uscore, iscore = [],[]
        for leftout_ind in itertools.combination(data_num,self.kd):
            ref = [training_data[i] for i in list(leftout_ind)]
            train2 = [training_data[i] for i in sample_numbers
                            if not i in list(leftout_ind)]
            rden = process_latencies(ref,kdensity,None)
            tden = process_latencies(train2,kdensity,None)
            uscore.append(difference(rden,tden))
            iscore.append(difference(rden,tden))
        self.sumThresh,self.difThresh = determineThresh(uscore,iscore)
    def evaluate(self,val_data,training_data):
        rden = process_latencies(training_data,kdensity,None)
        tden = process_latencies(val_data,kdensity,None)
        return evaluateThresh(difference(rden,tden),difference(rden,tden),self.sumThresh,self.difThresh)

if __name__ == '__main__':
    from preprocessor import split_samples, load_data, filter_users_val
    from CV import CV

    test_data,pkd = filter_users_val(split_samples(load_data()))
    for u in test_data.keys():
        if u not in {'1227981','ADabongofo'}:
            del test_data[u]
    print test_data.keys()
    test_cv = CV(DensityAuth, test_data,pkd)
