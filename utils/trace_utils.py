

def get_intercepts(summary, random_key):
    
    '''Computes the individual intercepts by combining them with the the Intercept'''
    
    return summary.filter(like=random_key, axis=0) + summary.loc['Intercept']


def get_coefs(summary, main_key, random_key):
    
    '''Computes the individual coefficients by combining them with the the key of interest'''
    
    return summary.filter(like=random_key, axis=0) + summary.loc[main_key]
