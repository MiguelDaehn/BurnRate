from startup import *


def mot(id_motor):


    if id_motor == 0:
        prop = input('Propellant (KNSB,KNSU...): ').lower()
        Dt = float(input('Throat diameter [mm]: '))
        Rho_pct = float(input('Density as % of ideal: '))
        Ng = int(input('Number of propellant grains: '))
        L = float(input('Length of propellant grains [mm]: '))
        De = float(input('External Diameter of grain [mm]: '))
        Di = float(input('Inner Diameter of grain [mm]: '))
        nuc = float(input('Combustion efficiency  η (usually 0.95): '))

        csi = input('Core surface inhibited? [y/N]: ').lower()
        esi = input("Ends' surfaces inhibited? [y/N]: ").lower()
        osi = input("Outer surface inhibited? [Y/n]: ").lower()

        if csi == 'y':
            csi = 0
        else:
            csi = 1

        if esi == 'y':
            esi = 0
        else:
            esi = 1
        if osi == 'n':
            osi = 1
        else:
            osi = 0

        brka = input('Are you trying to obtain burn rate data from pressure data? (y/N)').lower()
        if brka == 'y' or brka == 'yes':
            p_min = float(input('Minimum chamber pressure [MPa]: '))
            p_max = float(input('Maximum chamber pressure [MPa]: '))
        else:
            p_min = 0
            p_max = 10

    if id_motor == 1:
        prop = 'knsb'
        Dt = 9.659
        Rho_pct = 0.95
        Ng = 4
        L = 50.0
        De = 45.0
        Di = 25.0
        p_min = 0
        p_max = 10
        csi, esi, osi = [1, 1, 0]

    if id_motor == 2:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / 1.923
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
        p_min = 0
        p_max = 10
        csi, esi, osi = [1, 1, 0]

    if id_motor == 3:
        prop = 'knsb'
        Dt = 9.659
        Rho_pct = 0.95
        Ng = 4
        L = 50.0
        De = 45.0
        Di = 25.0
        p_min = 0
        p_max = 10
        csi, esi, osi = [1, 1, 0]

    dp = dict_prop[prop]
    rhoideal = properties_table[0][dp]


    motor_data = ar([prop, Dt, Rho_pct, Ng, L, De, Di, p_min, p_max, csi, esi, osi])

    return motor_data