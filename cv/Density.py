import numpy as np
import statsmodels.api as sm
from scipy import stats
import itertools

from Authenticator import Authenticator, compute_best_threshold
from data_manip import to_lat_dict, process_latencies
from density_auth import kdensity,determineThresh,evaluateThresh,density_scoring


class DensityAuth(Authenticator):
    def __init__(self):
        self.scores = {}
        self.loss = lambda ipr, frr, gt, it: ipr+frr
        self.thresh = {}

    def estimate_model(self,inner_train,inner_val):
        self.inn_train_model = process_latencies(
                                to_lat_dict(inner_train),kdensity,lambda: 0)
        self.inn_val_model = process_latencies(to_lat_dict(inner_val),kdensity,lambda: 0)

    def score(self,inner_val):
        new_dd = density_scoring(self.inn_train_model,self.inn_val_model)
        if self.scores == {}:
            self.scores = new_bfs
        else:
            for u in new_bfs.keys():
                self.scores[u].extend(new_bfs[u])

    def compute_threshold(self):
        for u in scores.keys():
            self.thresh[u] = compute_best_threshold(scoers[u])

    def evaluate(self,val_data,training_data):
            score_dict = self.score(val_data)
            results = {u:evaluate_threshold(self.thresh[u], score_dict[u]) for u in self.thresh.keys()}
            return results


if __name__ == '__main__':
    from preprocessor import split_samples, load_data, filter_users_val
    from CV import CV

    test_data,pkd = filter_users_val(split_samples(load_data()))
    for u in test_data.keys():
        if u not in {'1227981','ADabongofo'}:
            del test_data[u]
            del pkd[u]
    print test_data.keys()
    test_cv = CV(DensityAuth, test_data,pkd)
    for i in test_cv.validate():
        print "fuck"
