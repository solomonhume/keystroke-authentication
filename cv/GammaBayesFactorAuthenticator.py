import collections as coll
import pprint

import pylab as P
import scipy.stats as stats

from Authenticator import Authenticator, compute_best_threshold, evaluate_threshold
from data_manip import to_lat_dict, process_latencies
from gamma_auth import compute_bayesfactors, compute_likelihoods

class GammaBFAuth(Authenticator):
    def __init__(self):
        self.params = {}
        self.thresh = {}
        self.loss = lambda ipr, frr, gt, it: ipr+frr

    def train(self, training_data):
        self.params = process_latencies(to_lat_dict(training_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda: (-1.,-1.,-1.)
        )
        
        bf_dict = compute_bayesfactors(compute_likelihoods(self.params, training_data))
        for u in bf_dict.keys():
            self.thresh[u] = compute_best_threshold(bf_dict[u], self.loss)


    def evaluate(self, val_data):
        vbf_dict = compute_bayesfactors(compute_likelihoods(self.params, val_data))
        results = {u:evaluate_threshold(self.thresh[u], vbf_dict[u]) for u in self.thresh.keys()}
        return results


if __name__=='__main__':
    from CV import CV
    from preprocessor import split_samples, load_data

    P.np.seterr(all='ignore')

    all_data = split_samples(load_data())
    for u in all_data.keys():
        if u not in ['1227981', 'ADabongofo', 'ADlyndak']:
            del all_data[u]
    fucker = CV(GammaBFAuth, all_data)
    for i in fucker.validate():
        print i
