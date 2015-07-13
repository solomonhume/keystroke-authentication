import numpy as np
import statsmodels.api as sm
from scipy import stats
import itertools

from Authenticator import Authenticator
from data_manip import to_lat_dict, process_latencies
from density_auth import kdensity,determineThresh,evaluateThresh


class DensityAuth(Authenticator):
    def __init__(self,kd):
        self.kd = kd
        self.scores = []

    def estimate_model(self,inner_train,inner_val):
        self.inn_train_model = process_latencies(inner_train,kdensity,None)
        self.inn_val_model = process_latencies(inner_val,kdensity,None)

    def compute_threshold
        pass

    def score(self,inner_val):
        """
        take the density differences of two digraphs, add them together for all
        digraphs for a given user, divide by number of shared diagraphs
        """
        scores = {u:[] for u in training_data.keys()}
        for u in self.inn_train_model:
            if u

    def evaluate(self,val_data,training_data):
        rden = process_latencies(training_data,kdensity,None)
        tden = process_latencies(val_data,kdensity,None)
        return evaluateThresh(difference(rden,tden),difference(rden,tden),self.sumThresh,self.difThresh)

    def

if __name__ == '__main__':
    from preprocessor import split_samples, load_data, filter_users_val
    from CV import CV

    test_data,pkd = filter_users_val(split_samples(load_data()))
    for u in test_data.keys():
        if u not in {'1227981','ADabongofo'}:
            del test_data[u]
    print test_data.keys()
    test_cv = CV(DensityAuth, test_data,pkd)
