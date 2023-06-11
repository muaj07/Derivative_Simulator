# Advanced Blockchain Research's Derivatives Simulator (DeSim)

The everlasting options simulation used the ETH daily index price data for the last 1 year, and generate daily random buyers and sellers for both call and Put options. Transction fee are deducted from both buyers and sellers, which is added to the protocol teasury. Also, a 2% cut of the daily funding fee paid by the buyers is transfer to the protocol teasury as generated revenue. When a buyer closes the position in profit, the buyer is paid from the protocol teasury.

The main steps of the simulators are: a) Randomly create buyers (for call and put options) with min and max given value; b) Randomly pick a strike price and contract size for each buyer; c) Randomly create sellers (for call and put options) with min and max given value; d) Randomly pick a strike price and contract size for each seller; e) Compute the daily mark price and daily funding fee based on the number of buyers and sellers; f) Compute the transction feee paid by both the buyers and sellers and update the teasury; g) Charge buyers for daily funding fee; h) Pay seller the 0.98% of the daily funding fee charged from buyers; i) Repeat the whole process till last day of the year; j) In the meanwhile close sellers and buyers positions when they are in significant profit or in significant loss.



### [UPDATED jan 18 by juan]


Based on the simulator code described above, we perform a very rudimentary Monte Carlo simulation in order to investigate the expected value of the  profit generted by the simulator over different realizations of possible scenarios.  We also and provide a naive, first approach for the computation of sensitivities of the profit wrt the asset.

To that end, we added the following codes: 

* `earning_path.py`, which contains the function `rev,fee,sens=forward(min_b,max_b,min_s,max_s,equal)`, which can be understood as a wrapper of Ajmal's code where:
    * `min_b`, `min_s` are the minimum number of buyers and sellers, 
    * `mas_b`, `max_s` are the maximum number of buyers and sellers, and
    * `equal` sets each daily realization of the number of buyers equal to the number of sellers.
    * `rev` corresponds to the total profit from a simulation (over a trading period of 1 year)
    * `fee` corresponds to the transaction profit from a simulation (over a trading period of 1 year)
    * `sens` corresponds to the sensitivity of profit wrt underlying price from a simulation (over a trading period of 1 year). This is based on the very simple code `simple_sensitivity.py`.
    
* `simple_model.py` This is the outer loop application which implements the Monte Carlo estimator for some given values of hyper-parameters (number of samples, scenarios, etc). It outputs the Monte Carlo estimators for total profit, transaction profit and sensitivities for the simulated model and plots the results. One can then use the results obtained from this model to compute, e.g., failue probabilities (i.e., $\mathbb{P}(\text{Daily Profit}<c)$, for some prescribed value $c$. 

