import numpy as np
import option as op
import misc  as misc

def update_and_compute_fees(player,position,total_longs,total_shorts,total_number_of_calls,total_number_of_puts,index_price):
    # first part: computes fees
    if np.size(index_price)==1:
        index_price=index_price
        time=1
    else:
        index_price=index_price[-1]
        time=len(index_price)
    #updates values of the player    
    player.daily_update(index_price,time)
    #computes funding fee
    funding_fee_constant=0.01 # this should live on a hyperbolic curve; f* g=k (as uniswap)
    funding_fee_coefficient=misc.compute_daily_coefficient(total_longs, total_shorts,funding_fee_constant)    
    # computes trx fee
    trx_fee_constant=0.1 # this should live on a hyperbolic curve; f* g=k (as uniswap)
    # mark price is just position price (for everlasting, number of options x price) x 1 ffc
    position_price=player.position_price
    mark_price=position_price*(1+funding_fee_coefficient)
    #this is just mark(funding fee), but keeping it like this for readibility
    funding_fee_collected=mark_price-position_price
    trx_fee=funding_fee_collected*trx_fee_constant
  
    player.trx_fee_paid=trx_fee
    #updates the funding fee paid or received to each player
    if position=='buyer':
        player.funding_fee_paid=funding_fee_collected
        player.margin=player.margin-player.funding_fee_paid
    if position=='seller':
        player.funding_fee_paid=funding_fee_collected-trx_fee
        player.margin=player.margin+player.funding_fee_paid-trx_fee      
    
    
    return player


def liquidate(player,index_price):
    
    #determines wheather a player should be liquidated
    return 
    


def liquidate_buyer(buyer,misliquidation_error=0.02):
    
 
    ''' criteria to liquidate/close: 
        
        
        * they are about to run out of collateral, does so probabilistically
            with probability given by 
            # P= 1- max[(current collateral)/(inital collateral),0]
        
        
        * they have paid more in fees than half of the payoff, terminates w.p
        
            P= 1-min((0.5 x payoff)/(paid fees),1)
            
            
        * The just got itm, in which case they choose to cash settle with some probability. Here we 
        have to pay them
            
    '''


    #---------------------OUT OF COLLATERAL------------------------------------------------------
    #checks first if deposit is about to go out
    collateral_at_time_0=buyer.initial_margin
    current_collateral=buyer.margin
    payoff=buyer.payoff

       # terminates contract with probability 1- max[(current collateral)/(inital collateral),0]
    probability_of_liquidation=1-np.max([current_collateral/collateral_at_time_0,0])
    #import pdb; pdb.set_trace()
    paid=0
    # attempts to liquidate. here we model misliquidation error to take into account 
    # possible delays and stuff
    removed=False
    if np.random.random()>misliquidation_error: #with probability 1-mle, we attempt to liquidate
        if np.random.random()<probability_of_liquidation:
            buyer.liquidated=True
            removed=True
            paid=0
    #import pdb; pdb.set_trace()
          
    #---------------------PAID TOO MUCH ------------------------------------------------------


    total_fees_paid=collateral_at_time_0-current_collateral
    termination_probability=1-np.min([0.5*payoff/total_fees_paid,1])
    if np.random.random()<termination_probability:
        buyer.liquidated=True
        removed=True
        paid=0
    
    #import pdb; pdb.set_trace()
    
    #---------------------CASH SETTLES ------------------------------------------------------
   
    
    
    # if buyer is itm and hasnt been liquidated
    if buyer.moneyness == 'itm' and buyer.liquidated==False:
        paid=buyer.payoff
        removed=True
        buyer.liquidated=True
    #import pdb; pdb.set_trace()
     
    return paid, buyer, removed      




def liquidate_seller(seller):   
    paid=0
    removed=False
    if seller.moneyness=='itm':
        paid=seller.payoff
        if seller.payoff>seller.margin:
            #import pdb; pdb.set_trace()
            paid=-(seller.payoff-seller.margin)
        
        
        
        
        removed=True
        
    return paid,seller,removed
        
    
                
        




    
def compute_all_funding_fees(index_price,all_buyers,all_sellers,total_longs,total_shorts,total_number_of_calls,total_number_of_puts):
    
    total_collected_fees=0
    total_paid_fees=0
    total_trx_fees=0
    removed_index_buyers=[]
    removed_index_seller=[]
    total_settlements_to_buyers=0
    total_settlements_from_sellers=0

    total_active_buyers_day=0
    total_active_sellers_day=0
    #This part is expensive
    
    
    #computes paymentes FROM buyers
    day=0
    for list_buyers_at_given_day in all_buyers:
        ind=0
        for individual_buyer in list_buyers_at_given_day:
            #computes the fees and updates
            individual_buyer=update_and_compute_fees(player=individual_buyer,
                                         position='buyer',
                                         total_longs=total_longs,
                                         total_shorts=total_shorts,
                                         total_number_of_calls=total_number_of_calls,
                                         total_number_of_puts=total_number_of_puts,
                                         index_price=index_price)
            total_trx_fees+=individual_buyer.trx_fee_paid
            all_buyers[day][ind]=individual_buyer
            total_collected_fees+=individual_buyer.funding_fee_paid
            
            
            #liquidates buyer, if true
            paid, individual_buyer, removed=liquidate_buyer(individual_buyer)
            total_settlements_to_buyers+=paid
            
            if removed==True:
                removed_index_buyers.append(ind)   
            
            ind+=1
        #import pdb; pdb.set_trace()
        #deletes removed entries
        all_buyers[day]=misc.delete_multiple_element(all_buyers[day], removed_index_buyers)
        #import pdb; pdb.set_trace()
        total_active_buyers_day+=len(all_buyers[day])    
        day+=1

        
    #computes payments TO sellers   
    day=0
    for list_sellers_at_given_day in all_sellers:
        ind=0
        for individual_seller in list_sellers_at_given_day:
            #computes the fees and updates
            individual_seller=update_and_compute_fees(
                                         player=individual_seller,
                                         position='seller',
                                         total_longs=total_longs,
                                         total_shorts=total_shorts,
                                         total_number_of_calls=total_number_of_calls,
                                         total_number_of_puts=total_number_of_puts,
                                         index_price=index_price)
            all_sellers[day][ind]=individual_seller
            total_paid_fees+=individual_seller.funding_fee_paid
            total_trx_fees+=individual_seller.trx_fee_paid
            paid,seller,removed=liquidate_seller(individual_seller)
            total_settlements_from_sellers+=paid
            if removed==True:
                removed_index_seller.append(ind)   
            

            ind+=1
        all_sellers[day]=misc.delete_multiple_element(all_sellers[day], removed_index_seller)
        #import pdb; pdb.set_trace()
        total_active_sellers_day+=len(all_sellers[day])  
        day+=1

 
    PnL_fees=total_collected_fees-total_paid_fees+total_trx_fees-total_settlements_to_buyers+total_settlements_from_sellers
    return PnL_fees,all_buyers,all_sellers,total_active_buyers_day,total_active_sellers_day
        
    
    









# def daily_mark_price(index_price,call_mark_price,put_mark_price,long_call_positions_list,long_put_positions_list,short_call_positions_list,short_put_positions_list,day=None,type_volatility='fixed'):
#     """
#     Calculate the daily funding fees paid to the sellers for 
#     the everlastings options.
#     Args:
#         index_price: The index price of the underlying asset on this day
#         call_mark_price:Initial list of daily mark price for all call options
#         put_mark_price: Initial list of daily mark price for all put options
#         long_call_positions_list: List of all buyer call positions strike price
#         long_put_positions_list: List of all buyer put positions strike price
#         short_call_positions_list: List of all sellers call positions strike price
#         short_put_positions_list: List of all sellers put positions strike price
#     Returns:
#         The updated mark price for call and put options
#     """

#     #gets sigma from misc 
#     sigma=misc.get_volatility_of_underlying(time=day,TYPE=type_volatility)
    
    
    
#     #--Finding longs and shorts for all the call options
#     for i, (longs,shorts) in enumerate (zip(long_call_positions_list,short_call_positions_list)):

#         """ 
#             creates the option object for each long-short contract
            
#         """
        
#         if longs['total_longs']>0: #only computes those with actual contracts
#             K=longs['strike_price']
#             # creates contract
#             contract=op.option(TYPE='call', strike=K,spot=index_price)
        
#             # computes the perpetual option price
#             mark_price=contract.price_everlast(sigma)

#             # computes funding fee based on supply/demand
#             funding_fee_constant=0.01 # this should live on a hyperbolic curve; f* g=k
#             funding_fee_coefficient=misc.compute_daily_coefficient(longs["total_longs"], shorts["total_shorts"],funding_fee_constant)    
    
            
            
#             if longs["total_longs"]>shorts["total_shorts"]:
#                 diff=longs["total_longs"]-shorts["total_shorts"]
#                 call_mark_price[i]["mark_price"]=round(mark_price*(1+(funding_fee_coefficient*diff)),2)
#             else:
#                 call_mark_price[i]["mark_price"]= mark_price
#     #--Finding longs and shorts for all the put options
#     for i, (longs,shorts) in enumerate (zip(long_put_positions_list,short_put_positions_list)):
#                     # computes funding fee based on supply/demand
#         funding_fee_constant=0.01 # this should live on a hyperbolic curve; f* g=k
#         funding_fee_coefficient=misc.compute_daily_coefficient(longs["total_longs"], shorts["total_shorts"],funding_fee_constant)    
    
            
#         K=longs['strike_price']
#         if longs['total_longs']>0: #only computes those with actual contracts

#             # creates contract
#             contract=op.option(TYPE='put', strike=K,spot=index_price)
        
#             # computes the perpetual option price
#             mark_price=contract.price_everlast(sigma)
#             if longs["total_longs"]>shorts["total_shorts"]:
#                 diff=longs["total_longs"]-shorts["total_shorts"]
#                 put_mark_price[i]["mark_price"]= round(mark_price*(1+(funding_fee_coefficient*diff)),2)
#             else:
#                 put_mark_price[i]["mark_price"]= mark_price

#     return call_mark_price, put_mark_price


    
# def daily_funding_fee(call_mark_price,put_mark_price,call_funding_fee,put_funding_fee, index_price):
#     """
#     Calculate the daily funding fees paid for the everlastings options.
#     Args:
#         call_mark_price: The mark price for call options
#         put_mark_price: The mark price for put options
#         call_funding_fee: List of initial funding fee for call options
#         put_funding_fee: List of initial funding fee for put options
#         index_price: The index price of the underlying asset on this day
#     Returns:
#         call_funding_fee:Updated list of daily funding fee for call options
#         put_funding_fee: Updated list of daily funding fee for put options
#     """
#     liquidity_coefficient=0.01
#     for i, call in enumerate (call_mark_price):
#         call_funding_fee[i]["funding_fee"]=round(liquidity_coefficient*(call["mark_price"]-index_price),2)
#     for i, put in enumerate (put_mark_price):
#         put_funding_fee[i]["funding_fee"]=round(liquidity_coefficient*(put["mark_price"]-index_price),2)
#     return call_funding_fee,put_funding_fee

# def daily_buyer_seller_fundingfee_difference(buyers_list,sellers_list, call_funding_fee,put_funding_fee, fraction):
#     """
#     Calculate the daily funding fees difference between the amount collected from
#     buyers of call and put options and the amount paid to sellers of options.
#     Args:
#         buyers_list: List of buyers
#         sellers_list: List of sellers
#         call_funding_fee: List of funding fee for call options
#         put_funding_fee: List of funding fee for put options
#         fraction: Fraction of the funding fee paid to the sellers
#     Returns:
#         The difference between collected and paid amounts
#     """
#     buyer_paid=0
#     seller_collected=0
#     call_index=[None]*len(call_funding_fee)
#     put_index=[None]*len(put_funding_fee)
#     for i, call in enumerate (call_funding_fee):
#         call_index[i]=call["strike"]
#     for i, put in enumerate (put_funding_fee):
#         put_index[i]=put["strike"]
#         #Sum all the funding fee paid by the buyers of call and put options
#     for day in buyers_list:
#         for buyer in day:
#             if buyer["option_type"]==0: #option_type 0 denotes Call option 
#                 buyer_paid+=round(buyer["size"]*call_funding_fee[call_index.index(buyer["strike"])]["funding_fee"],2)
#             elif buyer["option_type"]==1:#option type 1 denotes Put option
#                  buyer_paid+=round(buyer["size"]*put_funding_fee[put_index.index(buyer["strike"])]["funding_fee"],2)
#         #Sum all the funding fee collected by the sellers of call and put options
#     for day in sellers_list:
#         for seller in day:
#             if seller["option_type"]==0: #option_type 0 denotes Call option 
#                 seller_collected+=round(fraction*seller["size"]*call_funding_fee[call_index.index(seller["strike"])]["funding_fee"],2)
#             elif seller["option_type"]==1:#option type 1 denotes Put option
#                  seller_collected+=round(fraction*seller["size"]*put_funding_fee[put_index.index(seller["strike"])]["funding_fee"],2)
#     #print(f"Daily net difference between collected and paid funding fee:{buyer_paid-seller_collected}")
#     return (buyer_paid-seller_collected)

# def daily_teasury_update(daily_collected_fee,daily_total_payoff):
#     """
#     daily update the teasury.
#     Args:
#         daily_collected_fee: Total fee earned by the protcol on daily basis
#         daily_total_payoff: Total payoff paid by the protocol on daily basis
#     Returns:
#         net_value:daily net value of the protocol
#     """
#     received=0
#     paid=0
#     net_value=0
#     received= daily_collected_fee
#     paid=daily_total_payoff
#     net_value=received-paid
#     #print(f"Daily earned revenue:{received} Daily paid amount:{paid} Daily PnL:{net_value}")
#     return net_value
