import pylab as P
import scipy.stats as stats

# alpha -> c(alpha) for KS test
sig2c = {0.1 : 1.22,
         0.05 : 1.36,
         0.025 : 1.48,
         0.01 : 1.63,
         0.005 : 1.73,
         0.001 : 1.95
}

C_ALPHA = sig2c[0.05]

def ks_test(samp1, samp2, c_alpha):
    '''
    [latency] -> [latency] -> float -> bool
    returns true if samp1 could have been from the same distribution as samp2
    '''
    ks_stat, pval = stats.ks_2samp(samp1, samp2)
    n, n_ = len(samp1), len(samp2)
    return ks_stat <= c_alpha*P.np.sqrt( (n+n_) / n*n_ )


def compute_ks_score(params, samples, user_ls=None):
    '''
    takes a dictionary {users -> {ngraphs -> [latency]}}
    and a dictionary {users -> [{ngraphs -> [latency]}]}
    returns a dictionary {users -> [(KS-score, 1|0 (genuine/impostor))]}
    
    the score is the ratio of accepted KS-tests to all of the KS-tests
    (i.e. the shared digraphs)
    '''
    ks_score = {u:[]
                for u in (params.keys() if user_ls == None else user_ls)}

    for user_samples in samples.iteritems():
        current_user = user_samples[0]
        for samp in user_samples[1]:
            for u in ks_score.keys():
                shared_ngs = set(samp.keys()) & set(params[u].keys())
                ks_score[u].append(
                    ( (sum( int(ks_test(samp[ng], params[u][ng], C_ALPHA))
                           for ng in shared_ngs )) / float(shared_ngs),
                      int(u==current_user)
                      )
                )
    return ks_score
