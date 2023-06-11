#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import option as op
import misc as misc


def update_and_compute_fees(
    player,
    position,
    total_longs,
    total_shorts,
    total_number_of_calls,
    total_number_of_puts,
    index_price,
    ):
    '''
    This function comprises two parts. In the first one, we update the state 
    of each seller (i.e., valueof their contracts etc, and comute their funcding and trx fees 
    
    We update the state each player (buyer or seller) we update their position 

    Parameters
    ----------
    player : an individial Player objet (either buyer or seller).
    position : (str) either 'buyer' or 'seller'. This is the position of the player object
    total_longs : (int) total number of long positions
    total_shorts : (int) total number of short positions
    total_number_of_calls : (int) total number of calls
    total_number_of_puts : (int) total number of puts
    index_price : (float) price of the underlying at the current day

    Returns
    -------
    player : player object, gets updated

    '''

    # first part: computes fees

    if np.size(index_price) == 1:
        index_price = index_price
        time = 1
    else:
        index_price = index_price[-1]
        time = len(index_price)

    # updates values of the player

    player.daily_update(index_price, time)

    # computes funding fee

    funding_fee_constant = 0.01  # this should live on a hyperbolic curve; f* g=k (as uniswap)
    funding_fee_coefficient = \
        misc.compute_daily_coefficient(total_longs, total_shorts,
            funding_fee_constant)

    # computes trx fee

    trx_fee_constant = 0.1  # this should live on a hyperbolic curve; f* g=k (as uniswap)

    # mark price is just position price (for everlasting, number of options x price) x 1 ffc

    position_price = player.position_price
    mark_price = position_price * (1 + funding_fee_coefficient)

    # this is just mark(funding fee), but keeping it like this for readibility

    funding_fee_collected = mark_price - position_price
    trx_fee = funding_fee_collected * trx_fee_constant

    player.trx_fee_paid = trx_fee

    # updates the funding fee paid or received to each player

    if position == 'buyer':
        player.funding_fee_paid = funding_fee_collected
        player.margin = player.margin - player.funding_fee_paid
    if position == 'seller':
        player.funding_fee_paid = funding_fee_collected - trx_fee
        player.margin = player.margin + player.funding_fee_paid \
            - trx_fee

    return player


def liquidate_buyer(buyer, misliquidation_error=0.02):
    ''' 
    Here we liquiduidate a buyer sition using the following critera: 
        
        
    criteria to liquidate/close a position for a buyer: 
        
        
        * they are about to run out of collateral, does so probabilistically
            with probability given by 
            # P= 1- max[(current collateral)/(inital collateral),0]
        
        
        * they have paid more in fees than half of the payoff, terminates w.p
        
            P= 1-min((0.5 x payoff)/(paid fees),1)
            
            
        * The just got itm, in which case they choose to cash settle with some probability. Here we 
        have to pay them
    

    Parameters
    ----------
    buyer : an individial Player objec wih position='buyer'.
    misliquidation_error: (float). probability of not liquidating when it should have been liquidated

    Returns
    -------
    player : player object, gets updated

              
    '''

    # ---------------------OUT OF COLLATERAL------------------------------------------------------
    # checks first if deposit is about to go out

    collateral_at_time_0 = buyer.initial_margin
    current_collateral = buyer.margin
    payoff = buyer.payoff

       # terminates contract with probability 1- max[(current collateral)/(inital collateral),0]

    probability_of_liquidation = 1 - np.max([current_collateral
            / collateral_at_time_0, 0])

    # import pdb; pdb.set_trace()

    paid = 0

    # attempts to liquidate. here we model misliquidation error to take into account
    # possible delays and stuff

    removed = False
    if np.random.random() > misliquidation_error:  # with probability 1-mle, we attempt to liquidate
        if np.random.random() < probability_of_liquidation:
            buyer.liquidated = True
            removed = True
            paid = 0

    # import pdb; pdb.set_trace()

    # ---------------------PAID TOO MUCH ------------------------------------------------------

    total_fees_paid = collateral_at_time_0 - current_collateral
    termination_probability = 1 - np.min([0.5 * payoff
            / total_fees_paid, 1])
    if np.random.random() < termination_probability:
        buyer.liquidated = True
        removed = True
        paid = 0

    # import pdb; pdb.set_trace()

    # ---------------------CASH SETTLES ------------------------------------------------------

    # if buyer is itm and hasnt been liquidated

    if buyer.moneyness == 'itm' and buyer.liquidated == False:
        paid = buyer.payoff
        removed = True
        buyer.liquidated = True

    # import pdb; pdb.set_trace()

    return (paid, buyer, removed)


def liquidate_seller(seller, misliquidation_error=0.02):
    ''' 
    Here we liquiduidate aseller if they have to pay. We account for misliquidation errors 

    Parameters
    ----------
    seller: an individial Player objec wih position='seller'.
    misliquidation_error: (float). probability of not liquidating when it should have been liquidated

    Returns
    -------
    player : player object, gets updated

              
    '''

    paid = 0
    removed = False
    if seller.moneyness == 'itm':
        paid = seller.payoff
        if np.random.random() > misliquidation_error:
            if seller.payoff > seller.margin:

                # import pdb; pdb.set_trace()

                paid = -(seller.payoff - seller.margin)

            removed = True

    return (paid, seller, removed)


def compute_all_funding_fees(
    index_price,
    all_buyers,
    all_sellers,
    total_longs,
    total_shorts,
    total_number_of_calls,
    total_number_of_puts,
    ):
    '''
    This is the main function of this module. Here we iterate over all existing players and update them, collect fees, and liquidate the,

    Parameters
    ----------
    index_price : (float) price of the underlying at the current day
    all_buyers : (float) list of all buyers up until the current day 
    all_sallers : (float) list of all sellers up until the current day 
    total_longs : (int) total number of long positions
    total_shorts : (int) total number of short positions
    total_number_of_calls : (int) total number of calls
    total_number_of_puts : (int) total number of puts

    Returns
    -------
    PnL_fees= (float) total of collected and given payents
    all_buyers : (float) updaed list of all buyers up until the current day 
    all_sallers : (float) updated list of all sellers up until the current day
    total_day_active_buyers (int) cardinality of [all_buyers]
    total_day_active_sellers(int) cardinality of [all_sellers]
    '''

    total_collected_fees = 0
    total_paid_fees = 0
    total_trx_fees = 0
    removed_index_buyers = []
    removed_index_seller = []
    total_settlements_to_buyers = 0
    total_settlements_from_sellers = 0

    total_active_buyers_day = 0
    total_active_sellers_day = 0

    # This part is expensive

    # computes paymentes FROM buyers

    day = 0
    for list_buyers_at_given_day in all_buyers:
        ind = 0
        for individual_buyer in list_buyers_at_given_day:

            # computes the fees and updates

            individual_buyer = update_and_compute_fees(
                player=individual_buyer,
                position='buyer',
                total_longs=total_longs,
                total_shorts=total_shorts,
                total_number_of_calls=total_number_of_calls,
                total_number_of_puts=total_number_of_puts,
                index_price=index_price,
                )
            total_trx_fees += individual_buyer.trx_fee_paid
            all_buyers[day][ind] = individual_buyer
            total_collected_fees += individual_buyer.funding_fee_paid

            # liquidates buyer, if true

            (paid, individual_buyer, removed) = \
                liquidate_buyer(individual_buyer)
            total_settlements_to_buyers += paid

            if removed == True:
                removed_index_buyers.append(ind)

            ind += 1

        # import pdb; pdb.set_trace()
        # deletes removed entries

        all_buyers[day] = misc.delete_multiple_element(all_buyers[day],
                removed_index_buyers)

        # import pdb; pdb.set_trace()

        total_active_buyers_day += len(all_buyers[day])
        day += 1

    # computes payments TO sellers

    day = 0
    for list_sellers_at_given_day in all_sellers:
        ind = 0
        for individual_seller in list_sellers_at_given_day:

            # computes the fees and updates

            individual_seller = update_and_compute_fees(
                player=individual_seller,
                position='seller',
                total_longs=total_longs,
                total_shorts=total_shorts,
                total_number_of_calls=total_number_of_calls,
                total_number_of_puts=total_number_of_puts,
                index_price=index_price,
                )
            all_sellers[day][ind] = individual_seller
            total_paid_fees += individual_seller.funding_fee_paid
            total_trx_fees += individual_seller.trx_fee_paid
            (paid, seller, removed) = \
                liquidate_seller(individual_seller)
            total_settlements_from_sellers += paid
            if removed == True:
                removed_index_seller.append(ind)

            ind += 1
        all_sellers[day] = \
            misc.delete_multiple_element(all_sellers[day],
                removed_index_seller)

        # import pdb; pdb.set_trace()

        total_active_sellers_day += len(all_sellers[day])
        day += 1

    PnL_fees = total_collected_fees - total_paid_fees + total_trx_fees \
        - total_settlements_to_buyers + total_settlements_from_sellers
    return (PnL_fees, all_buyers, all_sellers, total_active_buyers_day,
            total_active_sellers_day)
