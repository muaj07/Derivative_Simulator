#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a collection of misc functions

@author: juan
"""


import numpy as np
import scipy.stats
#removes indices
def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
    return list_object


def correlation(x, y):
    """ Return R where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value
def sample_strikes(index_price,option_type='call'):
    
    if np.size(index_price)>1:
        index_price=index_price[-1]
    
    strike_list=np.arange(1000,6000,200) # fixed this
    #list of strike price for put options
    #finds closest index to strike:
    pos=np.argmin(np.abs(strike_list-index_price))
    #gives a weight to the position
    weights=2.0**(-np.arange(1,10))
    weights=np.concatenate((weights,[1-np.sum(weights)]))
    # samples position:
    cdf=np.cumsum(weights)
    random_shift=np.argmax(np.random.random(1)<cdf)
    #slight skew towards OTM:
    if option_type=='call':
        skew_parameter=0.6
    elif option_type=='put':
        skew_parameter=0.4

    
    if np.random.random()<skew_parameter:
        new_pos=pos+random_shift
        if new_pos>len(strike_list)-1:
            new_pos=-1
    else:
        new_pos=pos-random_shift
        if new_pos<0:
            new_pos=0
    return strike_list[new_pos]
 
def compute_pull_call_ratio(index_price, lag=None):
    '''
    This is a measure of the market mood, defining the ratio of #puts/#calls
    If market is bearish, then $#calls>#pulls
    
    Since Nc+Np=N and Np/Nc=r then probability of put=r/(1+r). 
    Here we model r=0.5*(1-rho), with rho the correlation coef (-1,1) fo the last lag days
    
    to that end, we estimate the trend of the market based on the the las lag (default =7) days
    

    Parameters
    ----------
    index_price : TYPE
        list of prices until the current dat
    lag: TYPE
        how many days to llok back in the apst to compute the sentiment.

    Returns
    -------
    probability of setting a put.

    '''
    
    if lag==None:
        lag=7
    
    if np.size(index_price)<lag:
        proportion_puts=0.5
    else:
        recent_index=index_price[-lag:] #takes the price from the last lag days
        rho=correlation(np.arange(recent_index), recent_index) # computes correlation in [-1,1]
        #computes ratio with the simple formula  r=(1-rho)/2
        r=(1-rho*0.5)
        proportion_puts=r/(1+r)
    return proportion_puts
       
    
def compute_daily_coefficient(number_A,number_B,constant=0.01):
    '''
    dynamically computes the daily funding coefficient. If there's a lot of buyers, then coef increases.
    This same model is used for the IMT/OTM coefficients and liquidity coef.

    Parameters
    ----------
    number_A : TOTAL number of buyers
        DESCRIPTION.
    number_B : TOTAL number of sellers
        DESCRIPTION.
    constant : TYPE, optional
        DESCRIPTION. The default is 0.01.

    Returns
    -------
    daily funding coefficient

    '''
    # the model is coef * (1-prop buyers)=constant. Thus, if there are too many buyers, coef goes up.
    prop=number_A/(number_B+number_A)
    coef=0.5*constant/prop
    return coef
    




def get_volatility_of_underlying(time,TYPE='fixed'):
    """
    
    

    Parameters
    ----------
    time : TYPE integer, this is the day on the simulation
        DESCRIPTION.
    TYPE : TYPE, optional, 'list', 'oracle', or 'fixed'
        DESCRIPTION. The default is 'list', looks the volatility from a 
                    file. otherwise looks it up form an oracle (to implement)

    Returns
    -------
    None.

    """
    
    if TYPE=='list':
        raise TypeError('oracle type not implemented')
        
    if TYPE=='oracle':
        raise TypeError('oracle type not implemented')    
     
    if TYPE=='fixed':
        sigma=0.6
    return sigma
    
     
        
        
        