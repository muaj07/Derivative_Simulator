 
def long_options_list():
    """
    Create strike price list for long call and put positions.
    Args:

    Returns:
        long_call_positions_list: List of all buyer call positions strike price
        long_put_positions_list: List of all buyer put positions strike price
    """
    long_call_positions_list=[]
    long_put_positions_list=[]
    #list of strike price for call options 
    call_strike_list=[2000,2500,3000,3500,4000,4500,5000]
     #list of strike price for put options
    put_strike_list=[1000,1500,2000,2500,3000]
    for i in call_strike_list:
        long_call_positions_list.append({
            "strike_price":i,
            "total_longs":0
        })
    for i in put_strike_list:
        long_put_positions_list.append({
            "strike_price":i,
            "total_longs":0
        })
    return long_call_positions_list,long_put_positions_list


def short_options_list():
    """
    Create strike price list for short call and put positions.
    Args:

    Returns:
        short_call_positions_list: List of all seller call positions strike price
        short_put_positions_list: List of all seller put positions strike price
    """
    #list of strike price for call options
    call_strike_list=[2000,2500,3000,3500,4000,4500,5000]
    #list of strike price for put options
    put_strike_list=[1000,1500,2000,2500,3000]
    short_call_positions_list=[]
    short_put_positions_list=[]
    for i in call_strike_list:
        short_call_positions_list.append({
            "strike_price":i,
            "total_shorts":0
        })
    for i in put_strike_list:
            short_put_positions_list.append({
            "strike_price":i,
            "total_shorts":0
        })
    return short_call_positions_list,short_put_positions_list

def mark_price_list(long_call_positions_list,long_put_positions_list):
    """
    Create the mark price list for long call and put options.
    Args:
        long_call_positions_list: List of all buyer call positions strike price
        long_put_positions_list: List of all buyer put positions strike price
    Returns:
        call_mark_price: The mark price for call options
        put_mark_price: The mark price for sell options
    """
    call_mark_price=[]
    put_mark_price=[]
    for strike_price in long_call_positions_list:
        call_mark_price.append({
            "strike":strike_price["strike_price"],
            "mark_price": 0
            })
    for strike_price in long_put_positions_list:
        put_mark_price.append({
            "strike":strike_price["strike_price"],
            "mark_price": 0
            })
    return call_mark_price,put_mark_price

def funding_fee_list(long_call_positions_list,long_put_positions_list):
    """
    Create the funding fee list for long call and put options.
    Args:
        long_call_positions_list: List of all buyer call positions strike price
        long_put_positions_list: List of all buyer put positions strike price
    Returns:
        call_funding_fee: The funding fee for call options
        put_funding_fee: The funding fee for sell options
    """
    call_funding_fee=[]
    put_funding_fee=[]
    for strike_price in long_call_positions_list:
        call_funding_fee.append({
            "strike":strike_price["strike_price"],
            "funding_fee": 0
            })
    for strike_price in long_put_positions_list:
        put_funding_fee.append({
            "strike":strike_price["strike_price"],
            "funding_fee": 0
            })
    return call_funding_fee,put_funding_fee

def daily_mark_price(index_price,call_mark_price,put_mark_price,long_call_positions_list,long_put_positions_list,short_call_positions_list,short_put_positions_list):
    """
    Calculate the daily funding fees paid to the sellers for 
    the everlastings options.
    Args:
        index_price: The index price of the underlying asset on this day
        call_mark_price:Initial list of daily mark price for all call options
        put_mark_price: Initial list of daily mark price for all put options
        long_call_positions_list: List of all buyer call positions strike price
        long_put_positions_list: List of all buyer put positions strike price
        short_call_positions_list: List of all sellers call positions strike price
        short_put_positions_list: List of all sellers put positions strike price
    Returns:
        The updated mark price for call and put options
    """
    funding_fee_coefficient=0.01
    #--Finding longs and shorts for all the call options
    for i, (longs,shorts) in enumerate (zip(long_call_positions_list,short_call_positions_list)):
        if longs["total_longs"]>shorts["total_shorts"]:
            diff=longs["total_longs"]-shorts["total_shorts"]
            call_mark_price[i]["mark_price"]=round(index_price*(1+(funding_fee_coefficient*diff)),2)
        else:
            call_mark_price[i]["mark_price"]= index_price
    #--Finding longs and shorts for all the put options
    for i, (longs,shorts) in enumerate (zip(long_put_positions_list,short_put_positions_list)):
        if longs["total_longs"]>shorts["total_shorts"]:
            diff=longs["total_longs"]-shorts["total_shorts"]
            put_mark_price[i]["mark_price"]= round(index_price*(1+(funding_fee_coefficient*diff)),2)
        else:
            put_mark_price[i]["mark_price"]= index_price
    return call_mark_price, put_mark_price


    
def daily_funding_fee(call_mark_price,put_mark_price,call_funding_fee,put_funding_fee, index_price):
    """
    Calculate the daily funding fees paid for the everlastings options.
    Args:
        call_mark_price: The mark price for call options
        put_mark_price: The mark price for put options
        call_funding_fee: List of initial funding fee for call options
        put_funding_fee: List of initial funding fee for put options
        index_price: The index price of the underlying asset on this day
    Returns:
        call_funding_fee:Updated list of daily funding fee for call options
        put_funding_fee: Updated list of daily funding fee for put options
    """
    liquidity_coefficient=0.01
    for i, call in enumerate (call_mark_price):
        call_funding_fee[i]["funding_fee"]=round(liquidity_coefficient*(call["mark_price"]-index_price),2)
    for i, put in enumerate (put_mark_price):
        put_funding_fee[i]["funding_fee"]=round(liquidity_coefficient*(put["mark_price"]-index_price),2)
    return call_funding_fee,put_funding_fee

def daily_buyer_seller_fundingfee_difference(buyers_list,sellers_list, call_funding_fee,put_funding_fee, fraction):
    """
    Calculate the daily funding fees difference between the amount collected from
    buyers of call and put options and the amount paid to sellers of options.
    Args:
        buyers_list: List of buyers
        sellers_list: List of sellers
        call_funding_fee: List of funding fee for call options
        put_funding_fee: List of funding fee for put options
        fraction: Fraction of the funding fee paid to the sellers
    Returns:
        The difference between collected and paid amounts
    """
    buyer_paid=0
    seller_collected=0
    call_index=[None]*len(call_funding_fee)
    put_index=[None]*len(put_funding_fee)
    for i, call in enumerate (call_funding_fee):
        call_index[i]=call["strike"]
    for i, put in enumerate (put_funding_fee):
        put_index[i]=put["strike"]
        #Sum all the funding fee paid by the buyers of call and put options
    for day in buyers_list:
        for buyer in day:
            if buyer["option_type"]==0: #option_type 0 denotes Call option 
                buyer_paid+=round(buyer["size"]*call_funding_fee[call_index.index(buyer["strike"])]["funding_fee"],2)
            elif buyer["option_type"]==1:#option type 1 denotes Put option
                 buyer_paid+=round(buyer["size"]*put_funding_fee[put_index.index(buyer["strike"])]["funding_fee"],2)
        #Sum all the funding fee collected by the sellers of call and put options
    for day in sellers_list:
        for seller in day:
            if seller["option_type"]==0: #option_type 0 denotes Call option 
                seller_collected+=round(fraction*seller["size"]*call_funding_fee[call_index.index(seller["strike"])]["funding_fee"],2)
            elif seller["option_type"]==1:#option type 1 denotes Put option
                 seller_collected+=round(fraction*seller["size"]*put_funding_fee[put_index.index(seller["strike"])]["funding_fee"],2)
    #print(f"Daily net difference between collected and paid funding fee:{buyer_paid-seller_collected}")
    return (buyer_paid-seller_collected)

def daily_teasury_update(daily_collected_fee,daily_total_payoff):
    """
    daily update the teasury.
    Args:
        daily_collected_fee: Total fee earned by the protcol on daily basis
        daily_total_payoff: Total payoff paid by the protocol on daily basis
    Returns:
        net_value:daily net value of the protocol
    """
    received=0
    paid=0
    net_value=0
    received= daily_collected_fee
    paid=daily_total_payoff
    net_value=received-paid
    #print(f"Daily earned revenue:{received} Daily paid amount:{paid} Daily PnL:{net_value}")
    return net_value
