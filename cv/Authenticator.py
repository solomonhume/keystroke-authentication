from abc import ABCMeta, abstractmethod
import itertools

import pylab as P


class Authenticator(object):
    __metaclass__ = ABCMeta
    '''
    def aggregate_scores(self, training_data, kd):

        takes a dict {user -> [{ngraph -> [latency]}]}
        and a dict {user -> (k (int)}
        returns {user -> [ (score, 1|0) ]}

        loops over leave-k-out partitions of each user's data

        scores = {u:[] for u in training_data.keys()}
        for partition in itertools.product(
                *[partition_data(u, training_data[u], kd[u])
                  for u in training_data.keys()]
        ):
            print 'inner val'
            train = {x[0]:x[1] for x in list(partition)}
            val = {x[0]:x[2] for x in list(partition)}

            self.estimate_model(train)
            new_scores = self.score(val)
            for u in new_scores.keys(): scores[u].extend(new_scores[u])

        return scores
    '''
    @abstractmethod
    def estimate_model(self, training_data, val_data):
        pass

    @abstractmethod
    def compute_threshold(self):
        pass

    @abstractmethod    
    def score(self, inner_val):
        pass

    @abstractmethod
    def evaluate(self, val_data):
        pass


def evaluate_threshold(threshold, scores):
    '''
    takes a numerical scores threshold
    and a list of pairs of numerical scores and 1|0
    where 1 indicates a positive and 0 is a negative

    returns ipr,frr,# genuine tests, # impostor tests when marking all scores less than or equal to
    threshold as negatives
    '''
    ip,fr,gt,it = 0,0,0,0
    thresholded = [(int(threshold <= x[0]), x[1]) for x in scores]
    for i in thresholded:
        if   i[0] == 0 and i[1] == 0:
            it += 1
        elif i[0] == 0 and i[1] == 1:
            gt += 1
            fr += 1
        elif i[0] == 1 and i[1] == 0:
            it += 1
            ip += 1
        elif i[0] == 1 and i[1] == 1:
            gt += 1
    return float(ip)/it, float(fr)/gt, gt, it


def compute_best_threshold(scores, loss):
    '''
    takes [(score, 1|0)] and
    function loss(ipr, frr, gt, it)
    chooses the best score in the list to
    minimize result of loss

    returns threshold score.
    '''
    best_loss = P.np.inf
    best_score = scores[0][0]
    for t in scores:
        new_l = loss(*evaluate_threshold(t[0], scores))
        if new_l < best_loss:
            best_loss = new_l
            best_score = t[0]
    return best_score
