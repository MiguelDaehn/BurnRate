from pressure import calculate_pressure_parameters
from startup import *
from burnrate import *
from thrust import calculate_thrust
from motors import *



# TODO:
#  0:
#  Add a function that takes initial parameters such as a Diameter
#  And returns ALL needed parameters that can be calculated quickly
#  In order to declutter other functions (having calculations in them that don't serve the main purpose)
#  1:
#  Change the updating of the values in the for loops from directly altering the formula
#  to using lambda functions, to keep it neat.
#  2:
#  Add SRM's calculation of optimal thoaat diameter for the pressure.
#  3:
#  Manipulate 'nuc' to reach the calculated value of c*
#  if calculating from experimental pressure values

def test_BRfrompressure(id_file,motor):
    p_min = motor[24].astype(float)
    p_max = motor[25].astype(float)

    Pc, BR, pars = BR_from_pressure(id_file, motor)
    plt.plot(Pc, target_func(Pc, *pars), '--')
    pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
       'Taxa de regressão em função da pressão',
       labelf=f'{pars[1]}·P^{pars[0]}', log=0,
       x0f=[0.95 * p_min, 1.0 * p_max],
       y0f=[0.95 * min(BR[np.where(BR > 0)]), 1.05 * max(BR[np.where(BR < 40)])])
    return 0

def main():

    test_BRmultiple = False
    test_pressure = False
    test_thrust = False

    id_motor = 2
    motor = mot(id_motor)
    id_file = "nakka"



    test_BRfrompressure(id_file,motor)


    if test_BRmultiple:
        Prange = np.linspace(0.12, 10, 10000)
        arrstr = ar(['knsb', 'knsu'])

        for rd in arrstr:
            Rd = ar([rdp(rd, p) for p in Prange])
            plt.plot(Prange, Rd)

        plt.xlabel('Pressure [MPa]');
        plt.ylabel('R_dot [mm/s]');
        plt.title('Rd Values vs Pressure')
        plt.legend();
        plt.grid()
        plt.show()

    # N = 834
    N = 100 * 20
    if test_pressure:
        t, Pc, k, tbout, r_avg, m_grain0 = calculate_pressure_parameters(int(N), motor)

    if test_thrust:
        F, Pc, t = calculate_thrust(N, motor, 0.85, 6.3)
        pl(t, Pc, 'Tempo [s]', 'Pressão na Câmara [MPa]',
           'Pressão na câmara em função do tempo', 'Pressão', [-0.05, None], [0, None])

        pl(t, F, 'Tempo [s]', 'Empuxo [N]',
           'Empuxo em função do tempo', 'F', [-0.05, None], [0, None])

    return 0


if __name__ == '__main__':
    main()
    print('\n\nPlease read the improvement suggestions at the beginning of the main.py script.\n\n')

