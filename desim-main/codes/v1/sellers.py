import random
import numpy as np

def daily_sellers_open(index_price,short_call_positions_list,short_put_positions_list,range_sellers=[20,50], equal_to_buyers=None):
    """
    Generate randomly the daily number of sellers for the everlastings
    options.
    Args:
        index_price: The index price of the underlying asset on this day
        short_call_positions_list: List of all sellers call positions strike price
        short_put_positions_list: List of all sellers put positions strike price
    Returns:
        sellers: The number of daily sellers 
        sellers_daily_list: list of the sellers, which stored:
          users order size
          users option type (Call or Put)
          users strike price 
          initial value for funding fee paid to the sellers
        short_call_positions_list: Updated list of strike price for all seller call positions 
        short_put_positions_list: Updated list of all strike price for seller put positions
    """
    #Min and Max number of daily sellers
    # I added this line --JP
    min_daily_seller=range_sellers[0]
    max_daily_seller=range_sellers[1]
    #Min and Max size of daily sellers options
    min_option_size=1
    max_option_size=5
    #Initializing lists for buyers
    call_strike_list=[]
    put_strike_list=[]
    call_index=[None]*len(short_call_positions_list)
    put_index=[None]*len(short_put_positions_list)
    for i, call in enumerate (short_call_positions_list):
        call_strike_list.append(call["strike_price"])
        call_index[i]=call["strike_price"]
    for i, put in enumerate (short_put_positions_list):
        put_strike_list.append(put["strike_price"])
        put_index[i]=put["strike_price"]
    sellers_daily_list=[]
    #create random number of daily sellers for call and put options
    
    if equal_to_buyers is None:
        sellers=random.randint(min_daily_seller, max_daily_seller)
    else:
        sellers=equal_to_buyers
    #print(f"Total number of sellers:{sellers}")
    #Generating details for daily sellers of call and put options
    for i in range(sellers):
        #Randomly select call or put option
        option_type=random.randint(0, 1)
        if option_type==0: #Call option
            #ensure that the choosen strike price be larger than the Index price for call option
            strike_price=random.choice([x for x in call_strike_list if x>index_price])
            #increament the number of call option sellers by 1
            short_call_positions_list[call_index.index(strike_price)]["total_shorts"]+=1
            sellers_daily_list.append({
                "n": i,
                "size": random.randint(min_option_size, max_option_size),
                "strike":strike_price,
                "option_type":0,
                "fundingfee_collected":0
            })
        else:#short option
            #ensure that the choosen strike price be smaller than the Index price for put option
            strike_price=random.choice([x for x in put_strike_list if x<index_price])
            #increament the number of put option sellers by 1
            short_put_positions_list[put_index.index(strike_price)]["total_shorts"]+=1
            sellers_daily_list.append({
                "n": i,
                "size": random.randint(min_option_size, max_option_size),
                "strike":strike_price,
                "option_type":1,
                "fundingfee_collected":0
            })
    #for i in short_call_positions_list:
        #print(f"Short call position list:{i}")
    #for i in short_put_positions_list:
        #print(f"Short put position list:{i}")
    return sellers,sellers_daily_list,short_call_positions_list,short_put_positions_list

def daily_sellers_close(sellers_list,index_price, max_price):
    """
    Closing the daily number of sellers options for the everlastings
    options.
    Args:
        sellers_list: List of all the sellers open positions
        index_price: The index price of the underlying asset on this day
        max_price: The max price for the underlying asset that is used as a reference
        for calculating the probability values for a biased coin used to close open 
        positions
    Returns:
        total_payoff: Total payoff paid by the protocol for the closed options
        daily_closed_sum: Total number of closed positions
        sellers_list: updated list of the sellers positions 
    """
    daily_closed_sum=0
    total_payoff=0
    trials=1 
    for day in sellers_list:
        before=len(day)
        #print(f"Index price: {index_price} Sellers length of list before update:{len(day)}")
        for seller in list(day):
            if seller["option_type"]==0: # Call option
                if seller["strike"] > index_price:#The contract is not in lose
                    prob_value=np.maximum(seller["fundingfee_collected"]/max_price,0)
                    if prob_value>1.0:
                        outcome=1
                    else:
                        outcome=np.random.binomial(trials,prob_value)
                    if outcome==1:
                        day.remove(seller)
            elif seller["option_type"]==1:#Put option
                if seller["strike"]< index_price: #The contract is not in lose
                    prob_value=np.maximum(seller["fundingfee_collected"]/max_price,0)
                    if prob_value>1.0:
                        outcome=1
                    else:
                        outcome=np.random.binomial(trials,prob_value)
                    if outcome==1:
                        day.remove(seller)
        after=len(day)
        daily_closed_sum+=(before-after)
        #print(f"Length of seller list after update:{len(day)}")
        #print(f"Daily seller close sum:{daily_closed_sum} Daily payoff to Sellers:{total_payoff}") 
    return total_payoff, daily_closed_sum, sellers_list

def daily_seller_trx_fee(index_price, sellers_detail, call_mark_price,put_mark_price):
    """
    Calculate the daily transaction fees for the daily sellers for the everlastings
    options.
    Args:
        index_price: The index price of the underlying asset on this day
        sellers_detail: List comprising info about daily sellers 
        call_mark_price: Mark price for call options on this day
        put_mark_price: Mark price for put options on this day
    Returns:
        total_fee: The daily total fee 
    """
    fee_oom_c=0.0015
    fee_itm_c=0.0015
    fee_oom_p=0.0015
    fee_itm_p=0.0015
    total_fee=0
    #print(f"Daily trx fee for sellers of options")
    call_index=[None]*len(call_mark_price)
    put_index=[None]*len(put_mark_price)
    for i, call in enumerate (call_mark_price):
        call_index[i]=call["strike"]
    for i, put in enumerate (put_mark_price):
        put_index[i]=put["strike"]
    for index in sellers_detail:
        if index["option_type"]==0: #Assume option_type 0 denotes Call option 
            if index["strike"]>index_price: #out-of-money
                total_fee+= fee_oom_c*index["size"]*call_mark_price[call_index.index(index["strike"])]["strike"]
            else: # in-the-money
                total_fee+= fee_itm_c*index["size"]*index_price
        elif index["option_type"]==1: #Assume option_type 1 denotes put option 
            if index["strike"]<index_price: #out-of-money
                total_fee+= fee_oom_p*index["size"]*index_price
            else: # in-the-money
                total_fee+= fee_itm_p*index["size"]*put_mark_price[put_index.index(index["strike"])]["strike"] 
    #print(f"Daily total fee for sellers:{total_fee}")
    return total_fee

def update_sellers_fundingfee_collected(sellers_list,call_funding_fee,put_funding_fee,fraction):
    """
    Calculate the daily funding fees paid to the sellers for 
    the everlastings options.
    Args:
        sellers_list: List of all the sellers
        call_funding_fee: Amount of daily funding fee for call options on this day 
        put_funding_fee: Amount of daily funding fee for put options on this day
        fraction: Fraction of the funding fee paied to the sellers of the options
    Returns:
        sellers_list: sellers list with the updated funding fee 
    """
    call_index=[None]*len(call_funding_fee)
    put_index=[None]*len(put_funding_fee)
    for i, call in enumerate (call_funding_fee):
        call_index[i]=call["strike"]
    for i, put in enumerate (put_funding_fee):
        put_index[i]=put["strike"]
    for day in sellers_list:
        for seller in day:
            if seller["option_type"]==0: #option_type 0 denotes Call option 
                seller["fundingfee_collected"]+=round(fraction*seller["size"]*call_funding_fee[call_index.index(seller["strike"])]["funding_fee"],2)
            elif seller["option_type"]==1:#option type 1 denotes Put option
                 seller["fundingfee_collected"]+=round(fraction*seller["size"]*put_funding_fee[put_index.index(seller["strike"])]["funding_fee"],2)
    return sellers_list