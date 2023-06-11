#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 21:04:55 2022

@author: juan

we run a simple Monte Carlo simulation for the option model

"""
import numpy as np
import matplotlib.pyplot as plt
from earning_path import forward

# defines some hiperparameters of the MC simulation
N_its=100
N_days=366
runs_funding_total_revenue=np.zeros((N_its,N_days))
runs_funding_trans_revenue=np.zeros((N_its,N_days))
runs_sensitivity=np.zeros((N_its,N_days-1))
Days=np.arange(N_days)

# parameters for the  simualtor
min_number_daily_buyers=20
max_number_daily__buyers=30
min_number_daily_sellers=20
max_number_daily_sellers=50
Force_equal=False
#-----------------------------------------------
#%%
# starts the Monte Carlo simulation
plt.figure(figsize=(28, 7), dpi=80)

for i in range(N_its):
    print('iteration number  '+str(i))
    runs_funding_total_revenue[i,:],runs_funding_trans_revenue[i,:], runs_sensitivity[i,:]=forward(min_number_daily_buyers,max_number_daily__buyers,min_number_daily_sellers,max_number_daily_sellers,Force_equal)
    plt.subplot(131)
    plt.plot(Days,runs_funding_total_revenue[i,:], color='lightgray')
    plt.subplot(132)
    plt.plot(Days,runs_funding_trans_revenue[i,:], color='lightgray')    
    plt.subplot(133)
    plt.plot(Days[1:],runs_sensitivity[i,:], color='lightgray')    


# obtains mean values and 95CI

# computes means
mean_total_rev=runs_funding_total_revenue.mean(0)
mean_trans_rev=runs_funding_trans_revenue.mean(0)
mean_sens=runs_sensitivity.mean(0)

# computes SD
std_total_rev=runs_funding_total_revenue.std(0)
std_trans_rev=runs_funding_trans_revenue.std(0)
std_sens=runs_sensitivity.std(0)

#CIs 95 for total rev
UB_total_rev= mean_total_rev+2.98*std_total_rev/np.sqrt(N_its)
LB_total_rev= mean_total_rev-2.98*std_total_rev/np.sqrt(N_its)

#CIs 95 for trans rev
UB_trans_rev= mean_trans_rev+2.98*std_trans_rev/np.sqrt(N_its)
LB_trans_rev= mean_trans_rev-2.98*std_trans_rev/np.sqrt(N_its)

#CIs 95 for sens
UB_sens= mean_sens+2.98*std_sens/np.sqrt(N_its)
LB_sens= mean_sens-2.98*std_sens/np.sqrt(N_its)


#plots results
plt.subplot(131)
plt.plot(Days,mean_total_rev, color='firebrick')
plt.plot(Days,UB_total_rev,'--', color='lightcoral')
plt.plot(Days,LB_total_rev,'--',color='lightcoral')
plt.title(r'Mean total daily return, $N=$'+str(N_its))
#plt.ylim([-10000,120000])
plt.subplot(132)
plt.plot(Days,mean_trans_rev, color='firebrick')
plt.plot(Days,UB_trans_rev,'--',color='lightcoral')
plt.plot(Days,LB_trans_rev,'--',color='lightcoral')
plt.title(r'Mean transactional daily return, $N=$'+str(N_its))
#plt.ylim([300,2500])


plt.subplot(133)
plt.plot(Days[1:],mean_sens, color='firebrick')
plt.plot(Days[1:],UB_sens,'--',color='lightcoral')
plt.plot(Days[1:],LB_sens,'--',color='lightcoral')
plt.title(r'Mean sensitivity, $N=$'+str(N_its))


plt.tight_layout()

plt.savefig('results/naive_MC_run.eps')




