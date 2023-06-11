import random
import numpy as np

def daily_buyers_open(index_price,long_call_positions_list,long_put_positions_list,range_buyers=[20,50]):
    """
    Generate randomly the daily number of buyers for the everlastings
    options.
    Args:
        index_price: The index price of the underlying asset on this day
        long_call_positions_list: List of strike price for all buyer call positions 
        long_put_positions_list: List of all strike price for buyer put positions
    Returns:
        buyers: The number of daily buyers 
        buyers_daily_list: List of the buyers, which stored:
         users order size
         users option type (Call or Put)
         users strike price 
         initial value for funding fee paid by the buyers
        long_call_positions_list: Updated list of strike price for all buyer call positions 
        long_put_positions_list: Updated list of all strike price for buyer put positions
    """
    #Min and Max number of daily buyers
    
    # I made these part of the default input --JP
    min_daily_buyer=range_buyers[0]
    max_daily_buyer=range_buyers[1]
    #Min and Max size of daily buyer positions
    min_option_size=1
    max_option_size=5
    #Initializing the lists for call and put strike prices
    call_strike_list=[]
    put_strike_list=[]
    call_index=[None]*len(long_call_positions_list)
    put_index=[None]*len(long_put_positions_list)
    for i, call in enumerate (long_call_positions_list):
        call_strike_list.append(call["strike_price"])
        call_index[i]=call["strike_price"]
    for i, put in enumerate (long_put_positions_list):
        put_strike_list.append(put["strike_price"])
        put_index[i]=put["strike_price"]
    buyers_daily_list=[]
    #create random number of daily buyers for call and put options
    buyers=random.randint(min_daily_buyer, max_daily_buyer)
    #print(f"Number of buyers:{buyers}")
    #Generating details for daily buyers of call and put options
    for i in range(buyers):
        #Randomly select call or put option
        option_type=random.randint(0,1)
        if option_type==0: #Call option
            #ensure that the choosen strike price be larger than the Index price for call option
            strike_price=random.choice([x for x in call_strike_list if x>index_price])
            #increament the number of call option buyers by 1
            long_call_positions_list[call_index.index(strike_price)]["total_longs"]+= 1
            buyers_daily_list.append({
                "n": i,
                "size": random.randint(min_option_size, max_option_size),
                "strike":strike_price,
                "option_type":0,
                "fundingfee_paid":0
                })
        else:#Put option
            #ensure that the choosen strike price be smaller than the Index price for put option
            strike_price=random.choice([x for x in put_strike_list if x<index_price])
            #increament the number of put option buyers by 1
            long_put_positions_list[put_index.index(strike_price)]["total_longs"]+=1
            buyers_daily_list.append({
                "n": i,
                "size": random.randint(min_option_size, max_option_size),
                "strike":strike_price,
                "option_type":1,
                "fundingfee_paid":0
            })
    #for i in long_call_positions_list:
        #print(f"Long call position list:{i}")
    #for i in long_put_positions_list:
        #print(f"Long put position list:{i}")
    return buyers,buyers_daily_list,long_call_positions_list,long_put_positions_list


def daily_buyers_close(buyers_list,index_price,max_price):
    """
    Closing the daily number of buyers options for the everlastings
    options.
    Args:
        buyers_list: List of all the buyers open positions
        index_price: The index price of the underlying asset on this day
        max_price: The max price for the underlying asset that is used as a reference
        for calculating the probability values for a biased coin used to close open 
        positions
    Returns:
        total_payoff: Total payoff paid by the protocol for the closed options
        daily_closed_sum: Total number of closed positions
        buyers_list: updated list of the buyers positions 
    """
    daily_closed_sum=0
    total_payoff=0
    trials=1    
    for day in buyers_list:
        before=len(day)
        #print(f"Index price: {index_price} Buyers length of list before update:{len(day)}")
        for buyer in list(day):
            if buyer["option_type"]==0: #Call option
                pay_off=np.maximum(index_price - buyer["strike"], 0)
                if buyer["fundingfee_paid"] < (pay_off*buyer["size"]):#The contract is ITM
                    prob_value=pay_off/max_price
                    if prob_value>1.0:
                        outcome=1
                    else:
                        outcome=np.random.binomial(trials,prob_value)
                    if outcome==1: #close the position
                        total_payoff+= pay_off*buyer["size"]
                        day.remove(buyer)
                else: #payoff is less than the funding fee paid so far by buyer
                    if buyer["fundingfee_paid"]>(0.5*max_price):#buyer paid funding fee great than half oF ETH ATH
                       # Close the buyer call position after paying more than half of ETH ATH
                        day.remove(buyer)
            elif buyer["option_type"]==1:#Put option
                pay_off = np.maximum(buyer["strike"]-index_price, 0)
                if buyer["fundingfee_paid"]<(pay_off*buyer["size"]): #The contract is ITM
                    prob_value=pay_off/max_price
                    if prob_value>1.0:
                        outcome=1
                    else:
                        outcome=np.random.binomial(trials,prob_value)
                    if outcome==1: #close the position
                        total_payoff+= pay_off*buyer["size"]
                        day.remove(buyer)
                else: #payoff is less than the funding fee paid so far by buyer
                    if buyer["fundingfee_paid"]>(0.5*max_price):#buyer paid funding fee great than half oF ETH ATH
                       # Close the buyer put position after paying more than half of ETH ATH
                        day.remove(buyer)
        after=len(day)
        daily_closed_sum+=(before-after)
        #print(f"Buyer length of list after update:{len(day)}")
        #print(f"Daily close sum:{daily_closed_sum} Daily payoff to buyers:{total_payoff}")
                    
    return total_payoff, daily_closed_sum,buyers_list

def daily_buyer_trx_fee(index_price,buyers_detail,call_mark_price,put_mark_price):
    """
    Calculate the daily transaction fees for the daily buyers for the everlastings
    options.
    Args:
        index_price: The index price of the underlying asset on this day
        buyers_detail: List comprising info about daily buyers 
        call_mark_price: Mark price for all call options on this day
        put_mark_price: Mark price for all put options on this day
        
    Returns:
        total_fee: The daily total fee 
    """
    fee_oom_c=0.0015
    fee_itm_c=0.0015
    fee_oom_p=0.0015
    fee_itm_p=0.0015
    total_fee=0
    call_index=[None]*len(call_mark_price)
    put_index=[None]*len(put_mark_price)
    for i, call in enumerate (call_mark_price):
        call_index[i]=call["strike"]
    for i, put in enumerate (put_mark_price):
        put_index[i]=put["strike"]
    for index in buyers_detail:
        if index["option_type"]==0: #option_type 0 denotes Call option 
            if index["strike"]>index_price: #out-of-money
                total_fee+= fee_oom_c*index["size"]*call_mark_price[call_index.index(index["strike"])]["strike"]
            else: # in-the-money
                total_fee+= fee_itm_c*index["size"]*index_price
        elif index["option_type"]==1: #option_type 1 denotes put option 
            if index["strike"]<index_price: #out-of-money
                total_fee+= fee_oom_p*index["size"]*index_price
            else: # in-the-money
                total_fee+= fee_itm_p*index["size"]*put_mark_price[put_index.index(index["strike"])]["strike"] 
    #print(f"Daily total fee for buyers:{total_fee}")
    return total_fee

def update_buyers_fundingfee_paid(buyers_list,call_funding_fee,put_funding_fee):
    """
    Calculate the daily funding fees the buyers have to pay for 
    the everlastings options.
    Args:
        buyer_list: List of all the buyers
        call_funding_fee: Amount of daily funding fee for call options on this day 
        put_funding_fee: Amount of daily funding fee for put options on this day 
    Returns:
        buyer_list: Buyers list with the updated funding fee 
    """
    call_index=[None]*len(call_funding_fee)
    put_index=[None]*len(put_funding_fee)
    for i, call in enumerate (call_funding_fee):
        call_index[i]=call["strike"]
    for i, put in enumerate (put_funding_fee):
        put_index[i]=put["strike"]
    for day in buyers_list:
        for buyer in day:
            if buyer["option_type"]==0: #option_type 0 denotes Call option 
                buyer["fundingfee_paid"]+=round(buyer["size"]*call_funding_fee[call_index.index(buyer["strike"])]["funding_fee"],2)
            elif buyer["option_type"]==1:#option type 1 denotes Put option
                 buyer["fundingfee_paid"]+=round(buyer["size"]*put_funding_fee[put_index.index(buyer["strike"])]["funding_fee"],2)
    return buyers_list
    