import matplotlib.pyplot as plt
import numpy as np

from pressure import calculate_pressure_parameters
from startup import *
from burnrate import *
from thrust import *
from motor import *

# TODO:
#  1:
#  Change the updating of the values in the for loops from directly altering the formula
#  to using lambda functions, to keep it neat.
#  2:
#  Add SRM's calculation of optimal thoaat diameter for the pressure.
#  3:
#  Correct the error, discontinuity that occurs
#  when pressure drops to 0. just set ds/dt = 0.
#  4:
#  log scale graph not working. is it because the graph is in MPa? shouldn't be, right?
#  5:
#  fit the power law https://www.youtube.com/watch?v=wujirumjHxU
#  6:
#  Add a function that takes initial parameters such as a Diametere
#  And returns ALL needed parameters that can be calculated quickly
#  In order to declutter other functions (having calculations in them that don't serve the main purpose)
#  7:
#  Kn depends on pressure. look at tables to the right of the first page of SRM
#  Kn of a certain pressure (our desired MEOP) is calculated. Kn = Ab/At -> At = Kn_max * Ab_max
#  8:
#  There's an error when you try to run plt_AeAt(N, array_AeAt, motor, eta_noz=0.85):
#  It seems that for some reason the thrust is getting multiplied, like 3000 N when it was supposed to be ~500
#  Ok apparently it surges when the expansion ratio goes above 9 or 10
#  9:
#  YOU NEED TO FIX THE CF (THRUST COEFFICIENT) SOONER RATHER THAN LATER THIS IS A SERIOUS ISSUE

def plt_m_grains(N,id_prop,arr_props,motor,eta_noz=0.85,AeAt=6.3):
    for prop in arr_props:
        motor[id_prop] = prop
        F,Pc,t,Cf = calculate_thrust(N,motor,eta_noz,AeAt)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t,Pc)
    plt.grid(True)
    plt.show()

def plt_AeAt(N,arr_aeat,motor,eta_noz=0.85):
    for aeat in arr_aeat:
        F,Pc,t,Cf = calculate_thrust(N,motor,eta_noz,aeat)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t, Cf)
    plt.grid(True)
    plt.show()

def main():

    # Discretization

    # N = 834 #Discretization used by SRM, useful for checking / comparing values
    N = 100 * 20


    # Motor identification and definition

    id_file = "q2OM" # Another option would be 'nakka'. Change id_motor to 2, accordingly, for accurate results

    id_motor = 1
    motor = mot(id_motor)

    # array_L = np.linspace(20,60,10)
    # id_prop = 4
    # plt_m_grains(N,id_prop,array_L,motor,eta_noz=0.85,AeAt=6.3)

    # array_AeAt = np.linspace(1, 2, 100)
    # plt_AeAt(N, array_AeAt, motor, eta_noz=0.85)

    array_Di = np.linspace(5,35,100)
    id_prop = 6
    plt_m_grains(N,id_prop,array_Di,motor,eta_noz=0.85,AeAt=6.3)


    # Test functions

    # test_BR_from_pressure(id_file,id_motor,p_min=3.5,p_max=4.5)
    # test_br_multiple()
    t, Pc, k, tbout, r_avg, m_grain0 = calculate_pressure_parameters(int(N), motor)
    # thrust_pressure(N,motor,6.278)



    return 0


if __name__ == '__main__':
    main()
    print('\n\nPlease read the improvement suggestions at the beginning of the main.py script.\n\n')