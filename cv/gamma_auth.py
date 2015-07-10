import pylab as P
import scipy.stats as stats
import scipy.misc as misc

def log_gamma_likelihood(g_param, data):
    '''
    takes a triple (as returned from stats.gamma.fit) of gamma
    parameters 
    data is a list of latencies for the ngraph associated
    with the parameters
    '''
    if data == []: 
        return 0.
    if g_param[0] > 0 and g_param[2] > 0:
        return sum([stats.gamma.logpdf(x, 
                                       g_param[0], 
                                       scale=g_param[2], 
                                       loc=0) 
                    for x in data])
    return (P.np.log(1.) - P.np.log(480.))


def lat_dict2loglikelihood(lat_dict, param):
    '''
    takes a latency dictionary {ngraph -> [latency]}
    and a parameter dictionary {ngraph -> gamma param triple}
    returns the log likelihood

    assumes that p(ngraph) is uniform.
    '''
    return sum([log_gamma_likelihood(param[ng],
                                     lat_dict[ng])
                for ng in lat_dict.keys()])


def compute_likelihoods(params, samples):
    '''
    takes a dictionary {users -> {ngraphs -> parameters}}
    and a dictionary {users -> [{ngraphs -> [latency]}]}
    returns a dictionary {users -> [(likelihoods, 1|0 (genuine/impostor))]}
    '''
    ll_dict = {u:[] for u in params.keys()}
    # user_samples has type (user, [{ngraphs -> [latency]}])
    for user_samples in samples.iteritems():
        current_user = user_samples[0]
        for samp in user_samples[1]:
            for u in ll_dict.keys():
                ll_dict[u].append(
                    ( lat_dict2loglikelihood(samp, params[u]),
                      int(u==current_user) )
                )
    return ll_dict


def compute_bayesfactors(ll_dict):
    '''
    takes a dictionary {users -> [(likelihoods, 1|0 (genuine/impostor))]}
    returns a dictionary {users -> [(bayes factors, 1|0)]}
    '''
    bf_dict = {u:[] for u in ll_dict.keys()}
    for u in ll_dict.keys():
        for i in range(len(ll_dict[u])):
            impostor_lls = [ll_dict[impostor][i][0] 
                            for impostor in ll_dict.keys()
                            if impostor != u]
            l_impostor = misc.logsumexp(impostor_lls)
            l_genuine = ll_dict[u][i][0]
            bf_dict[u].append( 
                ((l_genuine-l_impostor), 
                 ll_dict[u][i][1]) 
            )
    return bf_dict
