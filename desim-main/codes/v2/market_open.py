import random
import misc as misc
import numpy as np
import players 

# defines an auxiliary class for random distributions
class default_distribution():
    '''
    this is an auxiliarry class for the creation of the default distr.


    Returns
    -------
    default distribution object; essentially a posiiton distr. with parameter lamnda. 
    '''
    def __init__(self,lamda):
        self.lamda=lamda
    def sample(self):
        return np.random.poisson(lam=self.lamda)
            
            
            
def daily_open(index_price_list,
               distribution_buyers=None,
               distribution_sellers=None,
               distribution_positions=None,
               lamda_buyers=50,
               lamda_sellers=50,
               lamda_pos=20,
               lag=None,
               kind_of_instrument='everlasting'):


    '''
    Generates new buyers and sellers. each of them are  objects of the players class

    Parameters
    ----------
    distribution_buyers: distribution object with method sample(). This is the distribution for the new number of buyers
    
    [optional]
    distribution_sellers: distribution object with method sample(). This is the distribution for the new number of sellers
    distribution_positions: distribution object with method sample(). This is the distribution for the number of contracts
    lambda_buyers: (int) parameter for the defualt dist. of buyers (poisson)
    lambda_sellers: (int) parameter for the defualt dist. of sellers(poisson)
    lambda_pos: (int) parameter for the defualt dist. of sellers(poisson)
    lag: (int) parameter to model the direction of the market based on the last (lag) readings. See misc.sample_strikes
    kinf_of_instrument: (str) whether the option is vanilla or everlasting 
    
    Returns
    -------
    
    new_daily_buyers= list of new daily buyers
    new_daily_sellers= list of new daily sellers
    total_number_calls= total number of calls opened that day
    total_number_puts= total number of puts opened that day
    
    
    '''

    
    
    # sets a distribution for buyers and positions
    if distribution_buyers==None: # if no input distribution it sets a poisson witgh rate lambda _default
        distribution_buyers=default_distribution(lamda_buyers)    
        
    # sets a distribution for buyers and positions
    if distribution_sellers==None: # if no input distribution it sets a poisson witgh rate lambda _default
        distribution_sellers=default_distribution(lamda_sellers)    
        
    if distribution_positions==None: # if no input distribution it sets a poisson witgh rate lambda _default
        distribution_positions=default_distribution(lamda_pos)   
     #------------------------------------------------------------------------   
               

    # samples number of buyers and sellers
    number_of_buyers=distribution_buyers.sample()
    number_of_sellers=distribution_sellers.sample()
    #obtains the largest number between buyers and sellers,this way we dont have to do 2 for loops
    
    max_number=max([number_of_buyers,number_of_sellers])
    
    new_daily_buyers=[]
    new_daily_sellers=[]

    total_number_puts=0
    total_number_calls=0


    for i in range(max_number):
        
        
#-------------------------Generates new buyers  -----------------------------------------------        
        if i<number_of_buyers:
            # defines the transaction side here
            transaction_side='buyer'
            
            # generates randomly how many positions are being open:
            number_of_positions=distribution_positions.sample()    
            
            
            # obtains the probability of a call or a put, and defines the type of option 
            prob_put=misc.compute_pull_call_ratio(np.array(index_price_list), lag=lag)
            if np.random.random()<prob_put:
                option_type='put'
                total_number_puts+=number_of_positions
            else:
                option_type='call'
                total_number_calls+=number_of_positions

            # selects a strike price:
            strike_price=misc.sample_strikes(np.array(index_price_list),option_type=option_type)
            #creates buyer:
            buyer=players.create_position(transaction_side=transaction_side,
                                    option_type=option_type,
                                    strike=strike_price,
                                    spot=np.array(index_price_list),
                                    number_of_contracts=number_of_positions,
                                    kind_of_instrument=kind_of_instrument,
                                    time=np.size(index_price_list))
            new_daily_buyers.append(buyer)
        

#-------------------------Generates new sellers  --------------------------------------------        
        
        if i<number_of_sellers:
            # defines the transaction side here
            transaction_side='seller'
            
            # generates randomly how many positions are being open:
            number_of_positions=distribution_positions.sample()    
            
            
            # obtains the probability of a call or a put, and defines the type of option 
            prob_put=misc.compute_pull_call_ratio(np.array(index_price_list), lag=lag)
            
            # this has the inverse effect as for the buyers case-- this creates some supply and demand 
            if np.random.random()>prob_put:
                option_type='put'
                total_number_puts+=number_of_positions
            else:
                option_type='call'
                total_number_calls+=number_of_positions

            # selects a strike price:
            strike_price=misc.sample_strikes(np.array(index_price_list),option_type=option_type)
            #creates seller:
            seller=players.create_position(transaction_side=transaction_side,
                                    option_type=option_type,
                                    strike=strike_price,
                                    spot=np.array(index_price_list),
                                    number_of_contracts=number_of_positions,
                                    kind_of_instrument=kind_of_instrument,
                                    time=np.size(index_price_list))
            new_daily_sellers.append(seller)        
            
        
    
   
    return new_daily_buyers,new_daily_sellers,total_number_calls,total_number_puts


    