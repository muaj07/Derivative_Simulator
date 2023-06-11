#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 17:04:35 2022

Here we price the everlasting option and the funding fee according to 


"""
import numpy as np
import matplotlib.pyplot as plt




class option:
    """ 
        we create an option class, this would make it easier to price down the line
        
    """


    def __init__(self,TYPE,strike,spot):
        
        
        # defines attributes to the option object
        self.TYPE=TYPE
        self.K=strike
        self.S=spot  #should be the values
        self.ITM=False
        
    """ Computes the payoff of the option"""    
    def compute_payoff(self):
        TYPE=self.TYPE
        S=self.S
        K=self.K
            
        if TYPE=='put':
       
            self.payoff=np.max((K-S,0))
  
        elif TYPE=='call':
            self.payoff=np.max((S-K,0))
        else:
            raise TypeError('Payoff for this option type is not implemented!')
        return self.payoff
    
    
    def price_everlast(self,sigma,T=1):
        
        TYPE=self.TYPE
        S=self.S
        K=self.K
        
        
        if TYPE=='call' or TYPE=='put': #the formula on WP
            """
            Formula on whitepaper only holds for vanilla put and calls..
            This assumes that $\sigma$ is constant, which, lol
            (see https://www.sciencedirect.com/science/article/abs/pii/S1042443121001359?dgcid=rss_sd_all)
            
            """
            #
            #computes u according to whitepaper
            u=np.sqrt(1+ 8/(sigma**2 *T) )
            
            #computes the so-called time value
            if S >= K:
                V=(K/u)*(S/K)**(-0.5*(u-1))
            else:
                V=(K/u)*(S/K)**(0.5*(u+1))
                
            price=self.compute_payoff()+V #computes price
        else: # if more exotic option
              
            raise TypeError('Price for this option type is not implemented!')
      
        return price
        
    
        
        
        

    
