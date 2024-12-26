from startup import *

def mot(id_motor):

    if id_motor==0:
        prop    = input('Propellant (KNSB,KNSU...): ').lower()
        Dt      = float(input('Throat diameter [mm]: '))
        Rho_pct = float(input('Density as % of ideal: '))
        Ng      = int(input('Number of propellant grains: '))
        L       = float(input('Length of propellant grains [mm]: '))
        De      = float(input('External Diameter of grain [mm]: '))
        Di      = float(input('Inner Diameter of grain [mm]: '))
        nuc      = float(input('Combustion efficiency  η (usually 0.95): '))

        csi = input('Core surface inhibited? [y/N]: ').lower()
        esi = input("Ends' surfaces inhibited? [y/N]: ").lower()
        osi = input("Outer surface inhibited? [Y/n]: ").lower()

        if csi ==  'y':
            csi = 0
        else:
            csi = 1

        if esi ==  'y':
            esi = 0
        else:
            esi = 1
        if osi ==  'n':
            osi = 1
        else:
            osi = 0

        brka    = input('Are you trying to obtain burn rate data from pressure data? (y/N)').lower()
        if brka=='y' or brka=='yes':
            p_min = float(input('Minimum chamber pressure [MPa]: '))
            p_max = float(input('Maximum chamber pressure [MPa]: '))
        else:
            p_min = 0
            p_max = 10

    elif id_motor == 1:
        prop = 'knsb'
        Dt = 9.659
        Rho_pct = 0.95
        Ng = 4
        L = 50.0
        De = 45.0
        Di = 25.0
        nuc = 0.95
        csi, esi, osi = [1, 1, 0]
        p_min = 3.85
        p_max = 4.3

    elif id_motor == 2:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / 1.923
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
        nuc = 0.95
        csi, esi, osi = [1, 1, 0]
        p_min = 3.5
        p_max = 5.5

    elif id_motor == 3:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / 1.923
        Ng = 2
        L = 65.0
        De = 50
        Di = 4
        nuc = 0.95
        csi, esi, osi = [1, 1, 0]
        p_min = 0
        p_max = 10

    else:
        print('Please input a valid motor id.')
        return 1


    dp = dict_prop[prop]
    rhoideal = properties_table[0][dp]
    rho_g = Rho_pct * rhoideal

    Lc = (Ng * L) * 1.2
    Vc = (Lc * (pi / 4) * De ** 2) / 1000 ** 3

    At = pi * (Dt / 2) ** 2
    Vg = pi * ((De / 2  / 10) ** 2 - (Di / 2 / 10) ** 2) * (L / 10)
    mp = Ng * Vg * rho_g

    rat = Ru / properties_table[2][dp]
    w0 = (De - Di) / 2

    to = nuc * properties_table[3][dp]
    ratto = rat * to
    k = properties_table[1][dp]
    c_star = np.sqrt(ratto / k * (((k + 1) / 2) ** ((k + 1) / (k - 1))))

    motor_data = ar([prop,      #00
                     Dt,        #01
                     Rho_pct,   #02
                     Ng,        #03
                     L,         #04
                     De,        #05
                     Di,        #06
                     w0,        #07
                     csi,       #08
                     esi,       #09
                     osi,       #10
                     dp,        #11
                     rhoideal,  #12
                     rho_g,     #13
                     Lc,        #14
                     Vc,        #15
                     At,        #16
                     Vg,        #17
                     mp,        #18
                     rat,       #19
                     to,        #20
                     ratto,     #21
                     k,         #22
                     c_star,    #23
                     p_min,     #24
                     p_max])    #25
    return motor_data