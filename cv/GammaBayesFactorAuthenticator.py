import collections as coll
import csv
import itertools
from time import strftime
import pprint

import pylab as P
import scipy.stats as stats

from Authenticator import Authenticator, compute_best_threshold, evaluate_threshold
from data_manip import to_lat_dict, process_latencies, partition_data
from gamma_auth import compute_bayesfactors, compute_likelihoods


class GammaBFAuth(Authenticator):
    def __init__(self):
        self.params = {}
        self.thresh = {}
        self.loss = lambda ipr, frr, gt, it: ipr+frr
        self.scores = {}

    def estimate_model(self, training_data):
        self.params = process_latencies(to_lat_dict(training_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda: (-1.,-1.,-1.)
        )


    def inner_validation(self, training_data, inner_val_data):
        self.estimate_model(training_data)
        new_scores = self.score(inner_val_data)
        if self.scores == {}:
            self.scores = new_scores
        else:
            for u in new_scores.keys():
                self.scores[u].extend(new_scores[u])


    def train(self, training_data, inner_val_data):
        #ll_dict = compute_likelihoods(self.params, training_data)
        #bf_dict = compute_bayesfactors(ll_dict)
        scores = {u:[] for u in training_data.keys()}

        print 'threshold computation'
        for u in scores.keys():
            self.thresh[u] = compute_best_threshold(scores[u], self.loss)


    def score(self, val_data):
        return compute_bayesfactors(compute_likelihoods(self.params, val_data))


    def evaluate(self, val_data):
        vbf_dict = self.score(val_data)
        #vbf_dict = compute_bayesfactors(compute_likelihoods(self.params, val_data))
        results = {u:evaluate_threshold(self.thresh[u], vbf_dict[u]) for u in self.thresh.keys()}
        return results


if __name__=='__main__':
    from CV import CV
    from preprocessor import split_samples, load_data, filter_users_val

    P.np.seterr(all='ignore')

    all_data, pkd = filter_users_val(split_samples(load_data()))
    for u in all_data.keys():
        if not u in {'1227981', '9999999'}:
            del all_data[u]
            del pkd[u]
    print all_data.keys()
    print pkd.keys()

    gbfa = CV(GammaBFAuth, all_data, pkd)

    with open('./bf_result.csv', 'rw+') as res_file:
        result_writer = csv.writer(res_file)
        
        for n,i in enumerate(gbfa.validate()):
            train_res, cv_res = i
            result_writer.writerow(['user', 
                                    'train_IPR', 'train_FRR', 'train_GT', 'train_IT', 
                                    'CV_IPR', 'CV_FRR', 'CV_GT', 'CV_IT'])
            for u in train_res.keys(): 
                result_writer.writerow([u] + 
                                       list(train_res[u]) + 
                                       list(cv_res[u]))
            result_writer.writerow([])
            print strftime("%H:%M:%S"), '- finished validation', n
