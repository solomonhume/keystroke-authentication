import itertools

import scipy.misc as misc

from Authenticator import Authenticator
from data_manip import partition_data, timestamp

class CV(object):
    '''
    implements truncated leave-p-out CV
    '''


    def __init__(self, auth, data, pkd):
        '''
        takes a dictionary (username -> [(ngraph -> [latencies])])
        username maps to list of samples (1k keystrokes) represented
        as dictionaries.

        '''
        self.data = data

        self.pkd = pkd
        self.p = {k:v[0] for k,v in pkd.items()}
        self.k = {k:v[1] for k,v in pkd.items()}

        self.auth = auth()


    def validate(self):
        '''
        takes (username -> [(n-graph -> [latencies])])
        returns a list of results from several partitions of the data
        '''
        for partition in itertools.product(
                *[partition_data(u, self.data[u], self.p[u])
                for u in self.data.keys()]
        ):
            train = {x[0]:x[1] for x in list(partition)}
            val = {x[0]:x[2] for x in list(partition)}
            for inner_part in itertools.product(
                    *[partition_data(u, train[u], self.k[u])
                      for u in train.keys()]
            ):
                inner_train = {x[0]:x[1] for x in list(inner_part)}
                inner_val = {x[0]:x[2] for x in list(inner_part)}
                self.auth.estimate_model(inner_train, inner_val)
                self.auth.score(inner_val)
            self.auth.estimate_model(train,val)
            self.auth.compute_threshold()
            yield self.auth.evaluate(train), self.auth.evaluate(val)
            self.auth.scores = {}
    
    def validate_user(self, u):
        timestamp('START validating user ' + u)
        # split the other user's data in half for training/validation
        # then just use these halves for all of the user's CV splits
        impostors = [x for x in self.data.keys() if x != u]
        inner_train = {x:[] for x in impostors}
        outer_train = {x:[] for x in impostors}
        inner_val = {x:[] for x in impostors}
        outer_val = {x:[] for x in impostors}
        for x in impostors:
            outer_val[x] = self.data[x][:self.p[x]]
            outer_train[x] = self.data[x][self.p[x]:]

            inner_val[x] = self.data[x][ self.p[x] : self.p[x]+self.k[x] ]
            inner_train[x] = self.data[x][ self.p[x]+self.k[x] : ]
        timestamp('constructed impostor sample partitions')

        print 'outer loop iterations:', int(misc.comb(len(self.data[u]), self.p[u]))
        print 'inner loop iterations:', int(misc.comb(len(self.data[u])-self.p[u], self.k[u]))

        impostor_params = None
        for n_outer, part in enumerate(partition_data(u, self.data[u], self.p[u])):
            # set the new partitions for this user
            outer_val[part[0]] = part[2]
            outer_train[part[0]] = part[1]
            for n_inner, inner_part in enumerate(partition_data(u, part[1], self.k[u])):
                inner_train[part[0]] = inner_part[1]
                inner_val[part[0]] = inner_part[2]
                
                self.auth.update_model(inner_train, [u])
                if n_inner == 0 and n_outer == 0:
                    self.auth.score(inner_val, [u])
                    inner_ll = self.auth.ll_dict
                else:
                    self.auth.ll_dict = inner_ll
                    self.auth.score(inner_val, [u], clear_cache=False)
                if n_inner % 5 == 0:
                    timestamp('finished inner loop iteration ' + str(n_inner))
            self.auth.compute_threshold()
            timestamp('finished threshold computation')
            self.auth.update_model(outer_train, [u])
            timestamp('finished final model estimation')

            #yield self.auth.evaluate(outer_train, user_ls=[u]), self.auth.evaluate(outer_val, user_ls=[u])
            yield self.auth.evaluate(outer_val, user_ls=[u])
            timestamp('finished outer loop iteration ' + str(n_outer))
            self.auth.scores = {}
