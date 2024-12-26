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



def main():

    # Motor identification and definition

    id_file = "q2OM" # Another option would be 'nakka'. Change id_motor to 2, accordingly, for accurate results
    id_motor = 0
    motor = mot(id_motor)


    # Discretization

    # N = 834 #Discretization used by SRM, useful for checking / comparing values
    N = 100 * 20


    # Test functions

    # test_BR_from_pressure(id_file,id_motor,p_min=3.5,p_max=4.5)
    test_br_multiple()
    t, Pc, k, tbout, r_avg, m_grain0 = calculate_pressure_parameters(int(N), motor)
    thrust_pressure(N,id_motor,6.278)



    return 0


if __name__ == '__main__':
    main()
    print('\n\nPlease read the improvement suggestions at the end of the main.py script.\n\n')