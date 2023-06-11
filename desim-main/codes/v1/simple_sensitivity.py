#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Ultra naive code to compute the sensitivity dF/dS, where

F: simulator (profit)
s: underlying (ETH, for example)

since F=F(S(t)) then dF/dt = dF(S(t))/dS * dS/dt,
which implies, (dF/dt)*(dS/dt)^{-1}=dF/dS


OFC this has a bunch a caveats since neither F nor S are differentiable in practice
(but let's pretend they are)


Created on Tue Jan 18 21:07:29 2022

@author: juan
"""


def compute_sensitivity(underlying,simulator):
    
    dSdt=(underlying[1:]-underlying[:-1])
    dFdt=(simulator[1:]-simulator[:-1])
    
    return dFdt/dSdt