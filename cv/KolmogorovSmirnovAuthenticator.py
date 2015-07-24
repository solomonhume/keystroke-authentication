import collections as coll
import csv
import itertools
import pprint

import pylab as P
import scipy.stats as stats

from Authenticator import Authenticator, compute_best_threshold, evaluate_threshold
from data_manip import to_lat_dict, process_latencies, partition_data

class KSTestAuth(Authenticator):
    def __init__(self, all_data):
        self.params = {}
        self.thresh = {}
        self.loss = lambda ipr, frr, gt, it: ipr+frr
        self.scores = {}
        # for compatibility, we ought to make a field for general caching or something
        self.ll_dict = None
        
        
    def estimate_model(self, training_data, val_data):
        self.params = to_lat_dict(training_data)

    
    def update_model(self, training_data, user_ls):
        '''
        optimization could be made to only merge user_ls's 
        latency dictionaries.
        '''
        self.params = to_lat_dict(training_data)
        
    
    def score(self, val_data, user_ls=None):
        new_scores = compute_ks_score(self.params, val_data, user_ls)
        if self.scores = {}:
            self.scores = new_scores
        else: 
            for u in new_scores.keys():
                self.scores[u].extend(new_scores[u])


    def compute_threshold(self):
        '''
        perhaps move this method into Authenticator.py
        '''
        for u in self.scores.keys():
            self.thresh[u] = compute_best_threshold(self.scores[u], self.loss)


    def evaluate(self, val_data):
        '''
        also consider moving this into Authenticator.py
        '''
        self.scores = {}
        self.score(val_data, user_ls)
        results = {u:evaluate_threshold(self.thresh[u], self.scores[u])
                   for u in (user_ls if (user_ls != None)
                             else self.thresh.keys())}
        return results

if __name__=='__main__':
    from CV import CV
    from preprocessor import split_samples, load_data, filter_users_val

    P.np.seterr(all='ignore')

    all_data, pkd = filter_users_val(split_samples(load_data()))

    for u in all_data.keys():
        if all_data[u] == []:
            del all_data[u]
            del pkd[u]


    ksta = CV(lambda: KSTestAuth(all_data), 
              all_data,
              pkd)

    with open('./bf_result.csv', 'rw+') as res_file:
        result_writer = csv.writer(res_file)
        result_writer.writerow(['user',
                                'CV_IPR', 'CV_FRR', 'CV_GT', 'CV_IT'])

        for n,i in enumerate(ksta.validate_user('1227981')):
            cv_res = i
            '''
            result_writer.writerow(['user',
                                    'train_IPR', 'train_FRR', 'train_GT', 'train_IT',
                                    'CV_IPR', 'CV_FRR', 'CV_GT', 'CV_IT'])

            for u in train_res.keys():
                result_writer.writerow([u] +
                                       list(train_res[u]) +
                                       list(cv_res[u]))
            '''
            result_writer.writerow(['1227981']+list(cv_res['1227981']))
