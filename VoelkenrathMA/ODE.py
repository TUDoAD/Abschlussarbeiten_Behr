# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 13:42:10 2023

@author: smmcvoel
"""
import time
import numpy as np
from scipy.integrate import solve_ivp, odeint

def ODESolver(y, x):
    # x - length reactor
    # y - concentration of species i
    k=[0.01458, 2199436443.16846, 0.01064, 117591068549.76498, 0.1163, 43271.93269101587, 6.288e-05, 34126.209306143486, 0.3737,
       0.007248713053254616, 2948977440.3028693, 24703.943627797853, 0.8419588727210624, 0.9756537024605241, 64028.03707632365,
       73721595257.95108, 691.367263119121, 1.8381873161299876e+20, 402902.2371366433, 593692.5671051844, 2088.262107584587,
       7.061427392644895e+20, 1607617409191675.0, 14669806446178.172, 2350491467748764.5, 9802674275893.83, 18309311139266.945,
       1786264513107753.2, 43977306830.82615, 4.395178449907699e+16, 1208988872564131.5, 10675524818.340195, 687261530.445125,
       0.006074635777584023, 2124303401.1446967, 1.29732197491555e+17, 2.833490280742555e+16, 3861974187.3059597, 39501811.0759406,
       1.4313159955922637e+18, 1.1355299533139845e-15, 1.5802739069877432e-10]
    
    dydx = np.zeros(20)
  
    dydx[0] = 0 # O2
    dydx[1] = - k[0]*y[6]*y[6]*y[1] + k[1]*y[7]*y[7] # H2
    dydx[2] = - k[2]*y[2]*y[6] + k[3]*y[8] # CH4
    dydx[3] = - k[4]*y[3]*y[6] + k[5]*y[9] # H2O
    dydx[4] = - k[6]*y[4]*y[6] + k[7]*y[10] # CO2
    dydx[5] = - k[8]*y[5]*y[6] + k[9]*y[11] # CO
    dydx[6] = - k[0]*y[6]*y[6]*y[1] + k[1]*y[7]*y[7] - k[2]*y[2]*y[6] + k[3]*y[8] - k[4]*y[3]*y[6] + k[5]*y[9] - k[6]*y[4]*y[6] + k[7]*y[10] - k[8]*y[5]*y[6] + k[9]*y[11] - k[10]*y[6]*y[10] + k[11]*y[12]*y[11] - k[12]*y[6]*y[11] + k[13]*y[12]*y[13] + k[16]*y[11]*y[7] - k[17]*y[15]*y[6] - k[18]*y[15]*y[6] + k[19]*y[12]*y[16] + k[20]*y[7]*y[13] - k[21]*y[6]*y[16] + k[22]*y[16]*y[7] - k[23]*y[17]*y[6] + k[24]*y[17]*y[7] - k[25]*y[18]*y[6] + k[26]*y[18]*y[7] - k[27]*y[6]*y[8] + k[28]*y[12]*y[7] - k[29]*y[14]*y[6] + k[30]*y[14]*y[7] - k[31]*y[6]*y[9] + k[34]*y[7]*y[10] - k[35]*y[19]*y[6] - k[36]*y[19]*y[6] + k[37]*y[14]*y[11] # Ni
    dydx[7] = + k[0]*y[6]*y[6]*y[1] - k[1]*y[7]*y[7] - k[14]*y[11]*y[7] + k[15]*y[14]*y[13] - k[16]*y[11]*y[7] + k[17]*y[15]*y[6] - k[20]*y[7]*y[13] + k[21]*y[6]*y[16] - k[22]*y[16]*y[7] + k[23]*y[17]*y[6] - k[24]*y[17]*y[7] + k[25]*y[18]*y[6] - k[26]*y[18]*y[7] + k[27]*y[6]*y[8] - k[28]*y[12]*y[7] + k[29]*y[14]*y[6] - k[30]*y[14]*y[7] + k[31]*y[6]*y[9] - k[34]*y[7]*y[10] + k[35]*y[19]*y[6] - k[38]*y[19]*y[7] + k[39]*y[15]*y[14] # H-Ni
    dydx[8] = + k[2]*y[2]*y[6] - k[3]*y[8] + k[26]*y[18]*y[7] - k[27]*y[6]*y[8] # CH4-Ni
    dydx[9] = + k[4]*y[3]*y[6] - k[5]*y[9] + k[30]*y[14]*y[7] - k[31]*y[6]*y[9] + k[32]*y[14]*y[14] - k[33]*y[12]*y[9] # H2O-Ni
    dydx[10]= + k[6]*y[4]*y[6] - k[7]*y[10] - k[10]*y[6]*y[10] + k[11]*y[12]*y[11] - k[34]*y[7]*y[10] + k[35]*y[19]*y[6] + k[40]*y[11]*y[11] - k[41]*y[13]*y[10] # CO2-Ni
    dydx[11]= + k[8]*y[5]*y[6] - k[9]*y[11] + k[10]*y[6]*y[10] - k[11]*y[12]*y[11] - k[12]*y[6]*y[11] + k[13]*y[12]*y[13] - k[14]*y[11]*y[7] + k[15]*y[14]*y[13] - k[16]*y[11]*y[7] + k[17]*y[15]*y[6] + k[36]*y[19]*y[6] - k[37]*y[14]*y[11] - k[40]*y[11]*y[11] + k[41]*y[13]*y[10]  # CO-Ni
    dydx[12]= + k[10]*y[6]*y[10] - k[11]*y[12]*y[11] + k[12]*y[6]*y[11] - k[13]*y[12]*y[13] + k[18]*y[15]*y[6] - k[19]*y[12]*y[16] - k[28]*y[12]*y[7] + k[29]*y[14]*y[6] + k[32]*y[14]*y[14] - k[33]*y[12]*y[9] # O-Ni
    dydx[13]= + k[12]*y[6]*y[11] - k[13]*y[12]*y[13] + k[14]*y[11]*y[7] - k[15]*y[14]*y[13] - k[20]*y[7]*y[13] + k[21]*y[6]*y[16] + k[40]*y[11]*y[11] - k[41]*y[13]*y[10] # C-Ni
    dydx[14]= + k[14]*y[11]*y[7] - k[15]*y[14]*y[13] + k[28]*y[12]*y[7] - k[29]*y[14]*y[6] - k[30]*y[14]*y[7] + k[31]*y[6]*y[9] - k[32]*y[14]*y[14] + k[33]*y[12]*y[9] + k[36]*y[19]*y[6] - k[37]*y[14]*y[11] + k[38]*y[19]*y[7] - k[39]*y[15]*y[14] # OH-Ni
    dydx[15]= + k[16]*y[11]*y[7] - k[17]*y[15]*y[6] - k[18]*y[15]*y[6] + k[19]*y[12]*y[16] + k[38]*y[19]*y[7] - k[39]*y[15]*y[14] # HCO-Ni
    dydx[16]= + k[18]*y[15]*y[6] - k[19]*y[12]*y[16] + k[20]*y[7]*y[13] - k[21]*y[6]*y[16] - k[22]*y[16]*y[7] + k[23]*y[17]*y[6] # CH-Ni
    dydx[17]= + k[22]*y[16]*y[7] - k[23]*y[17]*y[6] - k[24]*y[17]*y[7] + k[25]*y[18]*y[6] # CH2-Ni
    dydx[18]= + k[24]*y[17]*y[7] - k[25]*y[18]*y[6] - k[26]*y[18]*y[7] + k[27]*y[6]*y[8] # CH3-Ni
    dydx[19]= + k[34]*y[7]*y[10] - k[35]*y[19]*y[6] - k[36]*y[19]*y[6] + k[37]*y[14]*y[11] - k[38]*y[19]*y[7] + k[39]*y[15]*y[14] # COOH-Ni
    
    return dydx

start_time = time.time()

y0 = np.array([0.1, 1.0, 0.1, 0.1, 1.0, 0.1, 0.1, 0.1, 0.1, 0.1,
               0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
x_start = 0.0
x_end = 10.0

#solution = solve_ivp(ODESolver, (x_start, x_end), y0, x_eval=np.linspace(x_start, x_end, num=3))

x_eval=np.linspace(x_start, x_end, num=100)
solution = odeint(ODESolver, y0, x_eval)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Das Skript benötigte {elapsed_time:.2f} Sekunden, um durchzulaufen.")

