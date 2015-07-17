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
    def __init__(self, all_data):
        '''
        takes all data to estimate initial parameters.
        '''
        self.params = {}
        self.thresh = {}
        self.loss = lambda ipr, frr, gt, it: ipr+frr
        self.scores = {}
        
        self.estimate_model(all_data, None)


    def estimate_model(self, training_data, val_data):
        self.params = process_latencies(to_lat_dict(training_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda: (-1.,-1.,-1.)
        )

    def score(self, val_data):
        new_bfs = compute_bayesfactors(
            compute_likelihoods(self.params, val_data)
        )
        if self.scores == {}:
            self.scores = new_bfs
        else:
            for u in new_bfs.keys():
                self.scores[u].extend(new_bfs[u])


    def compute_threshold(self):
        for u in self.scores.keys():
            self.thresh[u] = compute_best_threshold(self.scores[u], self.loss)


    def evaluate(self, val_data):
        self.scores = {}
        self.score(val_data)
        vbf_dict = self.scores
        results = {u:evaluate_threshold(self.thresh[u], vbf_dict[u]) for u in self.thresh.keys()}
        return results


if __name__=='__main__':
    from pprint import PrettyPrinter

    from CV import CV
    from preprocessor import split_samples, load_data, filter_users_val

    P.np.seterr(all='ignore')
    pp = PrettyPrinter()

    all_data, pkd = filter_user_val(split_samples(load_data()))
    print all_data['1227981']

    gbfa = CV(lambda: GammaBFAuth(all_data), 
              all_data, 
              pkd)

    u,train,val = next(gbfa.validate_user('ADabongofo'))
    pp.pprint(u)
    pp.pprint(train)
    pp.pprint(val)
    '''
    with open('./bf_result.csv', 'rw+') as res_file:
        result_writer = csv.writer(res_file)
        print strftime("%H:%M:%S"), '- START'
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
    '''

