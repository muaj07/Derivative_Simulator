import numpy as np
import pandas as pd
from buyers import daily_buyers_open, daily_buyers_close,daily_buyer_trx_fee,update_buyers_fundingfee_paid
from sellers import daily_sellers_open, daily_sellers_close,daily_seller_trx_fee, update_sellers_fundingfee_collected
from fee import daily_mark_price,daily_funding_fee,long_options_list,short_options_list,mark_price_list,funding_fee_list,daily_teasury_update,daily_buyer_seller_fundingfee_difference
#from statistics import average_options, plot_daily_revenue,plot_remaining_active_positions,plot_active_positions
import  market_open
import fee_v2
import matplotlib.pyplot as plt  
if __name__=='main':
    # defines some hyperparameters 
    treasury_size_0=1E6
    # Protocol cut from funding fee collected from longs/buyers of options# Reading the daily ETH index price for last 1 year
    df = pd.read_csv('ETH-USD.csv')
    #daily index price for ETH
    daily_index_price=df['Close']
    
    days=len(daily_index_price)
    treasury_size=np.zeros(days)
    treasury_size[0]=treasury_size_0
    total_buyers=[]
    total_sellers=[]
    total_number_of_buyers=0
    total_number_of_sellers=0
    total_number_of_calls=0
    total_number_of_puts=0
    for d in range(days-1):
        #----------------------------- First part: Market opens -------------------
    
        # generates buyers and sellers at day d
        new_daily_buyers,new_daily_sellers,new_daily_calls,new_daily_puts=market_open.daily_open((daily_index_price[d+1]))
        # gets total number of buyers sellers and positions
        total_number_of_buyers+=np.size(new_daily_buyers)
        total_number_of_sellers+=np.size(new_daily_sellers)
        total_number_of_calls+=new_daily_calls
        total_number_of_puts+=new_daily_puts
        # appends to the list of existing buyers and sellers
        total_buyers.append(new_daily_buyers)
        total_sellers.append(new_daily_sellers)                                                    
        #----------------------------- Second part: computes fees -------------------
        # funding fees is computed for all buyers and sellers
        
        
        PnL_fees,total_buyers,total_sellers,active_buyers,active_sellers=fee_v2.compute_all_funding_fees(
            index_price=daily_index_price[d+1],
            all_buyers=total_buyers,
            all_sellers=total_sellers,
            total_longs=total_number_of_buyers,
            total_shorts=total_number_of_sellers,
            total_number_of_calls=total_number_of_calls,
            total_number_of_puts=total_number_of_puts)
        treasury_size[d+1]=treasury_size[d]+PnL_fees
        print('day {}, active sellers {}, active buyers {}, total PnL {}'.format(str(d),str(active_buyers), str(active_sellers),str(PnL_fees) ) )
        
        #print(PnL_fees)
    plt.plot(treasury_size)
        #--------------------------- third part: closes, updates and liquidates -------------------
        
    
    
    
    
    
