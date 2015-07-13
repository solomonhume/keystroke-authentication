import collections as coll
import csv
from time import strftime
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
        print strftime("%H:%M:%S"), '- training'
        
        print strftime("%H:%M:%S"), '- estimating parameters'
        self.params = process_latencies(to_lat_dict(training_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda: (-1.,-1.,-1.)
        )
        
        print strftime("%H:%M:%S"), '- computing Bayes factors'
        ll_dict = compute_likelihoods(self.params, training_data)
        bf_dict = compute_bayesfactors(ll_dict)
        
        print strftime("%H:%M:%S"), '- computing thresholds'
        for u in bf_dict.keys():
            self.thresh[u] = compute_best_threshold(bf_dict[u], self.loss)

        return bf_dict, ll_dict


    def evaluate(self, val_data):
        print strftime("%H:%M:%S"), '- evaluating'
        vbf_dict = compute_bayesfactors(compute_likelihoods(self.params, val_data))
        results = {u:evaluate_threshold(self.thresh[u], vbf_dict[u]) for u in self.thresh.keys()}
        return results


if __name__=='__main__':
    from CV import CV
    from preprocessor import split_samples, load_data

    P.np.seterr(all='ignore')

    all_data = split_samples(load_data())

    for u in all_data.keys():
        if u not in [#'ADcoiffaav',
                     '1227981',
                     'ADcavek',
                '''
                     'ADlyndak',
                     '1714733',
                     'ADshortnj',
                     'ADupperjk',
                     'ADabongofo',
                     'ADjiewang',
                     'ADmarsala' '''
                ]:
            del all_data[u]

    gbfa = CV(GammaBFAuth, all_data)

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
