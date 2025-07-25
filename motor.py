from startup import *

from dataclasses import dataclass
import numpy as np

@dataclass
class Motor:
    """Class representing a rocket motor"""
    prop: str          # e.g. 'knsu'
    Dt: float          # Throat diameter (mm)
    Rho_pct: float     # Density percentage
    Ng: int            # Number of grains
    L: float           # Grain length (mm)
    De: float          # Grain outer diameter (mm)
    Di: float          # Grain inner diameter (mm)
    p_min: float = 0   # Min pressure (MPa)
    p_max: float = 10  # Max pressure (MPa)
    csi: int = 1       # Core surface inhibition
    esi: int = 1       # End surface inhibition
    osi: int = 0       # Outer surface inhibition

    def to_array(self):
        """Convert to numpy array matching original format"""
        return np.array([
            self.prop, self.Dt, self.Rho_pct, self.Ng, self.L,
            self.De, self.Di, self.p_min, self.p_max,
            self.csi, self.esi, self.osi
        ], dtype=object)


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
        P_target = float(input('Target MEOP [MPa]: '))

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

    elif id_motor == 1:
        prop = 'knsb'
        Dt = 9.659
        Rho_pct = 0.95
        Ng = 4
        L = 50.0
        De = 45.0
        Di = 25.0
        p_min = 0
        p_max = 10
        P_target = 4.5
        csi, esi, osi = [1, 1, 0]

    elif id_motor == 2:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / 1.923
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
        p_min = 3.5
        p_max = 6
        P_target = 4.5
        csi, esi, osi = [1, 1, 0]

    elif id_motor == 3:
        prop = 'knsb'
        Dt = 9.659
        Rho_pct = 0.95
        Ng = 4
        L = 50.0
        De = 45.0
        Di = 25.0
        p_min = 0
        p_max = 10
        P_target = 4.5
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 4:
        prop = 'knsu'
        Dt = 5.0
        Rho_pct = 0.9
        Ng = 1
        L = 81.14
        De = 24.12
        Di = 5.0
        p_min = 0
        p_max = 10
        P_target = 2
        csi, esi, osi = [1, 0, 0]
    elif id_motor == 5:
        prop = 'knsu'
        Dt = 11
        Rho_pct = 0.85
        Ng = 1
        L = 80
        De = 33
        Di = 25.5
        p_min = 0
        p_max = 10
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 6:
        prop = 'knsu'
        Dt = 11
        Rho_pct = [0.85,0.88,0.9]
        Ng = 1
        L = 80
        De = 33
        Di = 25.5
        p_min = 0
        p_max = 10
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 7:
        prop = 'knsu'
        Dt = 6
        Rho_pct = 0.9533
        Ng = 1
        L = 75
        De = 25.4
        Di = 15.0
        p_min = 0
        p_max = 10
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 8:
        prop = 'knsu'
        Dt = 12.54
        Rho_pct = 0.8961
        Ng = 2
        L = (44.74+83.46)/2
        De = 48.34
        Di = 17.44
        p_min = 0
        p_max = 10
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 9:
        prop = 'knsu'
        Dt = 12.54
        Rho_pct = 0.9073
        Ng = 2
        L = (44.74+83.46)/2
        De = 48.34
        Di = 17.44
        p_min = 0
        p_max = 10
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    elif id_motor == 10:
        prop = 'knsu_geprop_02'
        Dt = 12.54
        Rho_pct = (0.89)
        Ng = 2
        L = (44.74+83.46)/2
        De = 48.34
        Di = 17.44
        p_min = 1.2
        p_max = 2
        P_target = 1.091
        csi, esi, osi = [1, 1, 0]
    else:
        id_motor_new = int(input('Please select one of the available motors, 1,2,3,4...: '))
        return mot(id_motor_new)
    prop = prop.lower()
    dp = dict_prop.get(prop, 2)  # Returns 2 if key doesn't exist
    if dp == 2:
        print(f"Warning: If you are not using KNSU, '{prop}' not found. Defaulting to dp = 2.")
    rhoideal = properties_table[0][dp]


    motor_data = ar([prop, Dt, Rho_pct, Ng, L, De, Di, p_min, p_max, csi, esi, osi])

    return motor_data