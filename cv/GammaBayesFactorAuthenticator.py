import collections as coll
import csv
import itertools
from time import strftime
import pprint

import pylab as P
import scipy.stats as stats

from Authenticator import Authenticator, compute_best_threshold, evaluate_threshold
from data_manip import to_lat_dict, process_latencies, partition_data
from gamma_auth import compute_bayesfactors, compute_bf_opt, compute_likelihoods


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


    def update_model(self, training_data, user_ls):
        '''
        update parameters for users in user_ls
        '''
        filtered_data = {u:training_data[u] for u in user_ls}
        new_param = process_latencies(to_lat_dict(filtered_data),
                                        lambda x: stats.gamma.fit(
                                            x, floc=0),
                                        lambda: (-1., -1., -1.)
        )
        for u in user_ls:
            self.params[u] = new_param[u]


    def score(self, val_data, user_ls=None):
        new_bfs = compute_bf_opt(
            compute_likelihoods(self.params, val_data),
            user_ls
        )
        if self.scores == {}:
            self.scores = new_bfs
        else:
            for u in new_bfs.keys():
                self.scores[u].extend(new_bfs[u])


    def compute_threshold(self):
        for u in self.scores.keys():
            self.thresh[u] = compute_best_threshold(self.scores[u], self.loss)


    def evaluate(self, val_data, user_ls=None):
        self.scores = {}
        self.score(val_data, user_ls)
        vbf_dict = self.scores
        results = {u:evaluate_threshold(self.thresh[u], vbf_dict[u]) 
                   for u in (user_ls if (user_ls != None) 
                             else self.thresh.keys())}
        return results


if __name__=='__main__':
    from pprint import PrettyPrinter

    from CV import CV
    from preprocessor import split_samples, load_data, filter_users_val

    P.np.seterr(all='ignore')
    pp = PrettyPrinter()

    all_data, pkd = filter_users_val(split_samples(load_data()))
    '''
    for u in all_data.keys():
        if not u in ['1227981', '9999999']:
            del all_data[u]
            del pkd[u]
    '''

    gbfa = CV(lambda: GammaBFAuth(all_data), 
              all_data, 
              pkd)

    with open('./bf_result.csv', 'rw+') as res_file:
        result_writer = csv.writer(res_file)
        print strftime("%H:%M:%S"), '- START'
        for n,i in enumerate(gbfa.validate_user('1227981')):
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
