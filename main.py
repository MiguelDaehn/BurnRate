from startup import *
from burnrate import *
from thrust import *
from motor import *
from plots import *


# TODO:
#  1:
#  Add SRM's calculation of optimal throat diameter for the pressure.
#  3:
#  Correct the error, discontinuity that occurs
#  when pressure drops to 0. just set ds/dt = 0.
#  4:
#  log scale graph not working. is it because the graph is in MPa? shouldn't be, right?
#  5:
#  Add a function that takes initial parameters such as a Diameter
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
#  10:
#  Add functionality to check if the user is separating KNSB grains with o-rings
#  11:
#  in the motor.py file, around line 100, add "P_target" to the motor_data array
#  12: make it so that 'motor' and 'grain' are significantly separate, with different classes

def main():

    # Discretization

    # N = 834 #Discretization used by SRM, useful for checking / comparing values
    N = 100000

    # Motor identification and definition--//--//---//--//---//--//---//--//--//--//---//--//---//--//---//--//

    id_file = "knsu_geprop_02";id_motor = 10
    # id_file = 'nakka'; id_motor = 2
    motor = mot(id_motor)

    # Finds the burn rate of a propellant given a .csv file with-------------------------------------------------------
    # time[s] and PRESSURE [MPa], a certain motor and a pressure range
    # test_BR_from_pressure(id_file,id_motor,p_min=1.2,p_max=2)

    # Plots burn rate as a function of pressure for the desired propellants--------------------------------------------
    # plot_br_multiple(ar(['knsu','knsu_geprop_02']), [0, 10])



    # Test functions---//--//---//--//---//--//---//--//---//--//---//--//---//--//---//--//---//--//--//--//---//--//


    # Testing with different propellants---------------------------------------------------------------------------------
    array_L = ar(['knsu','knsu_geprop_02']);id_prop = 0
    # plt_m_grains(N,id_prop,array_L,motor,eta_noz=0.85,AeAt=round((23.6/12.54)**2,2))

    # Test with 35 different inner diameter values for the grains-------------------------------------------------------
    # array_Di = np.linspace(5,35,100)
    # id_prop = 6
    # plt_m_grains(N,id_prop,array_Di,motor,eta_noz=0.85,AeAt=6.3)


    # Testing with varying expansion ratios -------------------------------------------------------------
    # array_AeAt = np.linspace(1, 6.5, 100)
    # plt_AeAt(N, array_AeAt, motor, eta_noz=0.85)



    # Regular functions ---//--//---//--//---//--//---//--//---//--//---//--//---//--//---//--//---//--//
    # Option 1: Using the Motor class
    # motor = Motor(
    #     prop='knsu',
    #     Dt=12.54,
    #     Rho_pct=0.89,
    #     Ng=2,
    #     L=(44.74 + 83.46) / 2,  # 64.1 mm
    #     De=48.34,
    #     Di=17.44,
    #     p_min=1.2,
    #     p_max=2.0
    # )

    create_eng=0
    if create_eng==1:
        t, Pc, k, tbout, r_avg, m_grain0 = calculate_pressure_parameters(int(N), motor)

        # AeAt = 6.278
        # AeAt = 2.39 #PVC_05
        AeAt = 1.505

        F, Pc_MPa, t, Cf = calculate_thrust(N,motor,0.9533,AeAt)
        data_01 = np.column_stack((t,F))
        nome_do_arquivo = 'GEPROP_001'
        info_01 = {'filename'           : nome_do_arquivo,
                   'name'               : nome_do_arquivo,
                   'outer_diameter'     : str(motor[5]),
                   'length'             : str(motor[4]),
                   'delay_charge_time'  : 'P',
                   'propellant_mass'    : str(m_grain0),
                   'total_mass'         : str(m_grain0),
                   'manufacturer'       : 'TauRocketTeam'}

        save_array_to_eng_file(data_01, info_01, path_thrustcurves)
        # Plots both Pressure and Thrust graphs-----------------------------------------------------------------------------
        # pl(t,F)
        # pl(t,Pc_MPa)
        # ic(max(F),max(Pc_MPa))



    return 0


if __name__ == '__main__':
    main()
    print('\n\nPlease read the improvement suggestions at the beginning of the main.py script.\n\n')