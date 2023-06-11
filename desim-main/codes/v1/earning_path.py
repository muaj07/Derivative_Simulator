#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 18 20:16:55 2022

@author: juan


Here we define the one run model of the simulator

"""


import numpy as np
import pandas as pd
from buyers import daily_buyers_open, daily_buyers_close,daily_buyer_trx_fee,update_buyers_fundingfee_paid
from sellers import daily_sellers_open, daily_sellers_close,daily_seller_trx_fee, update_sellers_fundingfee_collected
from fee import daily_mark_price,daily_funding_fee,long_options_list,short_options_list,mark_price_list,funding_fee_list,daily_teasury_update,daily_buyer_seller_fundingfee_difference
from simple_sensitivity import compute_sensitivity

def forward(NUM_BUYERS_MIN=20,NUM_BUYERS_MAX=50,NUM_SELLERS_MIN=20,NUM_SELLERS_MAX=50,FORCE_EQUAL=False):
    """
    
    DESCRIPTION:
     
     
     This is a very basic one-path simulation of a market of everlasting options. 
     It is essentially a wrapper for Ajmal's simulator. 
     
     
     INPUT:
    NUM_BUYERS_MIN=Minimum number of possible buyers per day. Default=20

    NUM_BUYERS_MAX=Maximum number of possible buyers per day. Default=50



    NUM_SELLERS_MIN=Minimum number of possible buyers per day. Default=20
    NUM_SELLERS_MAX=Maximum number of possible sellers per day. Default=50

    FORCE_EQUAL = Sets at every day number of buyers == number of sellers. Default= False
    
     OUTPUT: 
         
         * revenue
         * transaction fees
         * sensitivities
     
     
     NOTES: 
         
         * Here we are asumming that buyers~UNIFORM (NUM_BUYERS_MIN, NUM_BUYERS_MAX)
             i'd assume this is more of a poisson distribution. Same happens for sellers too.
             
             
          *  please add notes regarding modeling choices here.
     
    """

    buyers_list=[]
    sellers_list=[]
    call_mark_price=[]
    put_mark_price=[]
    call_funding_fee=[]
    put_funding_fee=[]
    markprice_list=[]
    fundingfee_list=[]
    long_call_positions_list=[]
    long_put_positions_list=[]
    short_call_positions_list=[]
    short_put_positions_list=[]
    protocol_daily_net_revenue=[]
    #Initial teasury balance
    teasury_size=1000000 
    # Protocol cut from funding fee collected from longs/buyers of options
    protocol_cut_from_fundingfee=0.02  
    # Funding fee paid to shorts/sellers of options
    fundingfee_for_sellers=1-protocol_cut_from_fundingfee
    # Reading the daily ETH index price for last 1 year
    df = pd.read_csv('ETH-USD.csv')
    #daily index price for ETH
    daily_index_price=df['Close']
    #initialized the list for daily trx fee charged from buyers and sellers of options
    daily_trx_fee= np.empty([2, len(daily_index_price)])
    daily_revenue=[None]*len(daily_index_price)
    #storing the daily opened and closed long and short positions
    open_long=[None]*len(daily_index_price)
    open_short=[None]*len(daily_index_price)
    close_long=[None]*len(daily_index_price)
    close_short=[None]*len(daily_index_price)
    
    # defines a range of buyers and sellers
    range_buyers=[NUM_BUYERS_MIN,NUM_BUYERS_MAX]
    range_sellers=[NUM_SELLERS_MIN,NUM_SELLERS_MAX]
    
    
    #print(f"Initial teasury size:{teasury_size}")
    for i in range(len(daily_index_price)):
        #print(f"Day number:{i}")
        if i==0: #Execute only once at the begining
            #create initial list of long (both call and put) options
            long_call_positions_list,long_put_positions_list=long_options_list()
            #create initial list of short (both call and put) options
            short_call_positions_list,short_put_positions_list=short_options_list()
            #create initial list of mark price for both call and put options
            call_mark_price,put_mark_price=mark_price_list(long_call_positions_list,long_put_positions_list)
            #create initial list of funding fee for both call and put options
            call_funding_fee,put_funding_fee=funding_fee_list(long_call_positions_list,long_put_positions_list)
        buyers_numbers, buyers_details,long_call_positions_list,long_put_positions_list=daily_buyers_open(daily_index_price[i],long_call_positions_list,long_put_positions_list,range_buyers)
        # decides whether we are simulating num buyers=num sellers
        if FORCE_EQUAL==True:
            sellers_numbers, sellers_details,short_call_positions_list,short_put_positions_list=daily_sellers_open(daily_index_price[i],short_call_positions_list,short_put_positions_list,range_sellers,buyers_numbers)
        else:
            sellers_numbers, sellers_details,short_call_positions_list,short_put_positions_list=daily_sellers_open(daily_index_price[i],short_call_positions_list,short_put_positions_list,range_sellers)
        buyers_list.append(buyers_details)
        sellers_list.append(sellers_details)
        #calculate daily mark price for call and put options
        call_mark_price,put_mark_price=daily_mark_price(daily_index_price[i],call_mark_price,put_mark_price,long_call_positions_list,long_put_positions_list,short_call_positions_list,short_put_positions_list)
        #calculate daily funding fee for call and put options
        call_funding_fee,put_funding_fee=daily_funding_fee(call_mark_price,put_mark_price,call_funding_fee,put_funding_fee,daily_index_price[i])
        #store the daily long and short open positions
        open_long[i]=buyers_numbers
        open_short[i]=sellers_numbers
        #Calculate the daily transction fee for buyer and seller options
        daily_trx_fee[0,i]=daily_buyer_trx_fee(daily_index_price[i],buyers_details,call_mark_price,put_mark_price)
        daily_trx_fee[1,i]=daily_seller_trx_fee(daily_index_price[i],sellers_details,call_mark_price,put_mark_price)
        buyers_list= update_buyers_fundingfee_paid(buyers_list,call_funding_fee,put_funding_fee)
        sellers_list= update_sellers_fundingfee_collected(sellers_list,call_funding_fee,put_funding_fee,fundingfee_for_sellers)
        funding_fee_diff=daily_buyer_seller_fundingfee_difference(buyers_list, sellers_list,call_funding_fee,put_funding_fee,fundingfee_for_sellers)
        daily_payoff_buyers, daily_closed_buyer_positions, buyers_list=daily_buyers_close(buyers_list,daily_index_price[i], daily_index_price.max())
        daily_payoff_sellers, daily_closed_seller_positions, sellers_list=daily_sellers_close(sellers_list,daily_index_price[i], daily_index_price.max())
        #Store the daily number of closed long and short closed positions
        close_long[i]=daily_closed_buyer_positions
        close_short[i]=daily_closed_seller_positions
        daily_revenue[i]=funding_fee_diff+daily_trx_fee[0,i]+daily_trx_fee[1,i] 
        protocol_daily_net_revenue.append(daily_teasury_update(daily_revenue[i],daily_payoff_buyers+daily_payoff_sellers))
    #net_long=sum(open_long)-sum(close_long)
    #net_short=sum(open_short)-sum(close_short)
    #print(f"Total Longs:{net_long} Total Shorts:{net_short} Teasury Size: {teasury_size+sum(protocol_daily_net_revenue)} Total net revenue:{sum(protocol_daily_net_revenue)}")
    #Average number of buyers per day
    #avg_buyers, avg_sellers= average_options(sum(open_long),sum(open_short),len(daily_index_price))
    #print(f"Average longs:{avg_buyers} Average shorts:{avg_sellers}")
    #plot_daily_revenue(daily_revenue, daily_trx_fee,daily_index_price)
    #plot_active_positions(open_long, close_long, open_short,close_short,len(daily_index_price))
    #plot_remaining_active_positions(buyers_list,sellers_list, len(daily_index_price))
    total_trx_fee= daily_trx_fee[0,:]+daily_trx_fee[1,:]
    
    # Computes naively the sensitivities w.r.t changes in underlying
    sensitivity=compute_sensitivity(daily_index_price.to_numpy(),np.array(daily_revenue) )
    return daily_revenue, total_trx_fee, sensitivity