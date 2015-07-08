import itertools

class CV(object):
    '''
    implements truncated leave-p-out CV
    '''
    
    def __init__(self, auth, data):
        '''
        takes a dictionary (username -> [(n-graph -> [latencies])])
        username maps to list of samples (1k keystrokes) represented
        as dictionaries.

        '''
        # TODO compute p
        self.data = data
        self.auth = auth

    
    def partition_data(self, u, samples, p):
        '''
        takes a username and list of dictionaries [(n-graph -> [latencies])]
        generates partitions l1, l2 [(n-graph -> [latencies])]
        so that len(l2) = p
        and returns u, l1, l2
        '''
        sample_numbers = xrange(len(samples))
        for leftout_ind in itertools.combinations(sample_numbers,p):
            val_samples = [ samples[i] 
                             for i in list(leftout_ind) ]
            train_samples = [ samples[i] 
                              for i in sample_numbers 
                              if not i in list(leftout_ind) ]
            yield u, train_samples, val_samples
        
    
    def validate(self, data):
        '''
        takes (username -> [(n-graph -> [latencies])])
        returns a list of results from several partitions of the data
        '''
        for partition in itertools.product(
                partition_data(u, self.data[u],p) for u in self.data.keys()
        ):
            
            train = {x[0]:x[1] for x in list(partition)}
            test = {x[0]:x[2] for x in list(partition)}
            
            self.auth.train(train)
            yield self.auth.evaluate(val)
