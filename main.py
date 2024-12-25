import numpy as np

from pressure import calculate_pressure_parameters
from startup import *
from burnrate import *

#TODO:
# 1:
# Correct the error, discontinuity that occurs
# when pressure drops to 0. just set ds/dt = 0.
# 2:
# log scale graph not working. is it because the graph is in MPa? shouldn't be, right?
# 3:
# fit the power law https://www.youtube.com/watch?v=wujirumjHxU



def main():

    testeNakka          = False
    testeRand           = False
    test_BRfrompressure = False
    test_BRmultiple     = False
    teste_pressure      = True

    id_file = "q2OM"



    p_min = 3.85
    p_max = 4.3

    #TODO:
    #Add a function that takes initial parameters such as a Diameter
    #And returns ALL needed parameters that can be calculated quickly
    #In order to declutter other functions (having calculations in them that don't serve the main purpose)

    prop = 'knsb'
    Dt = 9.659
    Rho_pct = 0.95
    Ng = 4
    L = 50.0
    De = 45.0
    Di = 25.0


    if testeNakka:
        prop = 'knpsb'
        dp = dict_prop[prop]
        rhoideal = ic(properties_table[0][dp])
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rhoideal
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
    elif(testeRand):
        prop = 'knpsb'
        dp = dict_prop[prop]
        rhoideal = ic(properties_table[0][dp])
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rhoideal
        Ng = 2
        L = 65.0
        De = 50
        Di = 4

    csi, esi,osi = [1,1,0]
    motor = ar([prop, Dt, Rho_pct, Ng, L, De, Di, p_min, p_max,csi,esi,osi])

    if test_BRfrompressure:
        Pc, BR, pars = BR_from_pressure(id_file, motor)
        plt.plot(Pc, target_func(Pc, *pars), '--')
        pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
           'Taxa de regressão em função da pressão',
           labelf=f'{pars[1]}·P^{pars[0]}', log=0,
           x0f=[0.95 * p_min, 1.0 * p_max],
           y0f=[0.95 * min(BR[np.where(BR>0)]), 1.05 * max(BR[np.where(BR<40)])])
    if test_BRmultiple:
        Prange = np.linspace(0.12,10,10000)
        arrstr = ar(['knsb','knsu'])

        for rd in arrstr:
            Rd = ar([rdp(rd,p) for p in Prange])
            plt.plot(Prange,Rd)

        plt.xlabel('Pressure [MPa]');plt.ylabel('R_dot [mm/s]');plt.title('Rd Values vs Pressure')
        plt.legend();plt.grid()
        plt.show()


    if teste_pressure:
        N = 834
        N = 100*20
        calculate_pressure_parameters(int(N), motor)

    return 0


if __name__ == '__main__':
    main()
