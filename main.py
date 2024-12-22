import numpy as np

from startup import *
from burnrate import *


def main():
    testeNakka = True

    id_file = "nakka"

    # testeNakka = False

    p_min = 3.0
    p_max = 5.5

    if testeNakka:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rho_prop[prop]
        Ng = 2
        L = 65.0
        De = 43.1
        Di = 13.88
    else:
        prop = 'knpsb'
        At = 81.1
        Dt = np.sqrt(At / (pi / 4)) * 10
        Rho_pct = 1.912 / rho_prop[prop]
        Ng = 2
        L = 65.0
        De = 50
        Di = 4

    motor = ar([prop, Dt, Rho_pct, Ng, L, De, Di, p_min, p_max])

    Pc, BR = BR_from_pressure(id_file, motor)

    pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]',
       'Taxa de regressão em função da pressão',
       labelf='Taxa de Regressão do grão', log=1,
       x0f=[0.9 * p_min, 1.0 * p_max],
       y0f=[0.9 * min(BR), 1.1 * max(BR)])

    return 0


if __name__ == '__main__':
    main()
