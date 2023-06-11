#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creates the player class. This will treat each individual buyer/seller, rather than the aggregate.
There should also be a counterpart class that will be the company
@author: juan
"""
import numpy as np
import option as op
import misc 



class create_position:
    def __init__(self,transaction_side,option_type,spot,strike,time,number_of_contracts,kind_of_instrument='everlasting',margin_mult=1.5):
        '''
        We are instantiating the player class. This will keep track of all the actions of the player

        Parameters
        ----------
        transaction_side : 'buyer' or 'seller'
            which side of the transacion you are on
        option_type : 'put' or 'call'. TODO: add more exotic types
            which type of contract  they are creating
        time : t, which day we are on (see if really needed)
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        
        self.liquidated=False # has this user been liquidated?
        self.transaction_side=transaction_side
        self.kind_of_instrument=kind_of_instrument
        self.option_type=option_type
        self.time=time
        self.funding_fee_paid=0
        self.trx_fee_paid=0

        self.spot=spot
        self.strike=strike
        self.time=time
        self.number_of_contracts=number_of_contracts
        self.margin_mult=margin_mult
        self.option=op.option(TYPE=self.option_type,strike=self.strike,spot=self.spot)


        self.position_price=self.price_position()
        self.margin=self.margin_mult*self.position_price
        self.initial_margin=self.margin

        if time>1:
            spot=spot[-1]
        
        
    def price_position(self):
        if self.kind_of_instrument=='everlasting':
            sigma=misc.get_volatility_of_underlying(time=self.time)

            price=self.number_of_contracts*self.option.price_everlast(sigma=sigma)
     
        elif self.kind_of_instrument=='vanilla':
            
            price=self.number_of_contracts*self.option.compute_payoff(self) # bi discounted interest rate, we assume 1day horizon
            
        return price
    
    def daily_update(self,spot,time):
        self.spot=spot
        self.time=time
        self.option=op.option(TYPE=self.option_type,strike=self.strike,spot=self.spot)

        self.position_price=self.price_position()
        self.payoff=self.position_price
        if self.option_type=='put':
            if self.strike>self.spot:
                self.moneyness='itm'
                self.payoff=(self.strike-self.spot)*self.number_of_contracts
            else:
                self.moneyness='otm'
        elif self.option_type=='call':
            if self.spot>self.strike:
                self.moneyness='itm'
                self.payoff=(self.spot-self.strike)*self.number_of_contracts
            else:
                self.moneyness='otm'
        
    
        

        
        
        
    
        
        
        