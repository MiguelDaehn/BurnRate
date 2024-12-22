from startup import *
from burnrate import *




def main():
    id_file = "nakka"



    #Dados do motor


    # Dados dos grãos

    prop = 'KNSU'
    Dt = 9.656
    Rho_pct = 0.95

    Ng = 4
    L = 50.0
    De = 45.0
    Di = 25.0




    #Nakka
    testeNakka = True
    if testeNakka:
        prop = 'knpsb'
        Ng=2
        Rho_pct = 1.912/rho_prop[prop]
        De=43.1
        Di=13.88
        L=65.0
        At=81.1
        Dt = np.sqrt(At/(pi/4))
        # w0=14.61
        # Vg = pi*((De/2/10)**2-(Di/2/10)**2)*(L/10)

    motor = ar([prop,Dt,Rho_pct,Ng,L,De,Di])

    Pc,BR = BR_from_pressure(id_file,motor)


    pl(Pc, BR, 'Pressão na Câmara [MPa]', 'Burn Rate [mm/s]', 'Taxa de regressão em função da pressão',labelf='Taxa de Regressão do grão')





    return 0




if __name__ == '__main__':
    main()
