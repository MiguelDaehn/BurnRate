import numpy as np

from startup import *


def Ab_f(N,De,Di0,L,s):
    A_b = pi*N*(0.5*(De**2-(Di0+2*s)**2)+(L-2*s)*(Di0+2*s))
    return A_b

def Delta_s(At,Ab,Pc,rho,cstar,delta_t):
    delta_s = (At*Pc*delta_t)/(Ab*rho*cstar)
    return delta_s
# Define the power series function
def power_series(x, *coeffs):
    return sum(c * x**i for i, c in enumerate(coeffs))


def main():
    path_csv = 'data/burnrate2.csv'
    data = np.loadtxt(path_csv, delimiter='\t', skiprows=1)  # skiprows=1 if there's a header
    T = data[:,0]
    Pc = (10**6)*data[:,1]
    # ic(Pc)
    delta_t = np.array([T[i+1]-T[i] for i in range(len(T)-1)])
    delta_t = np.append(delta_t,delta_t[-1])
    dt_avg = np.average(delta_t)

    #Dados do motor

    Dt = 9.656 #[mm]
    At = pi*(Dt/2)**2


    # Dados dos grãos

    Rho_ideal = 1.841
    Rho_pct = 0.95
    Rhog = Rho_ideal*Rho_pct

    Ng = 4
    L = 50.0
    De = 45.0
    Di = 25.0
    Vg = pi*((De/2/10)**2-(Di/2/10)**2)*(L/10)


    w0 = (De-Di)/2

    #Nakka
    testeNakka = False
    if testeNakka:
        Ng=2
        Rhog = 1.912
        De=43.1
        Di=13.88
        L=65.0
        At=81.1
        w0=14.61
        Vg = pi*((De/2/10)**2-(Di/2/10)**2)*(L/10)

    mp = Ng * Vg * Rhog


    # Outros
    Psum = np.sum(Pc)
    cstar = ((At / mp) * Psum * dt_avg)/1000


    err_w0 = 1.0

    Ab = np.zeros_like(T)
    s = np.zeros_like(T)
    delta_s=np.zeros_like(T)
    ds_dt=np.zeros_like(T)


    start = time.time()
    delta_s[1] = 0.1
    ss = np.array([0,5,100])/100
    while err_w0 > 0.000000000000001:
        s[1] = ss[1]
        for i,t in enumerate(T):

            Ab[i]       = Ab_f(Ng,De,Di,L,s[i-1])
            # ic(Ab[i])
            if i > 1:
                s[i] = s[i - 1] + delta_s[i - 1]
            if i>0:
                delta_s[i]  = Delta_s(At,Ab[i],Pc[i],Rhog,cstar,delta_t[i])
                ds_dt[i] = delta_s[i]/delta_t[i]
                # delta_s[i] = Delta_s(At, Ab[i], Pc[i], Rhog, cstar, dt_avg)
                # ds_dt[i] = delta_s[i] / dt_avg
                # ic(delta_s[i])


            # ic(s[-1])
        # if (s[-1] > w0):
        #     s0 = (s0+s0ant)/2
        # s0ant = s[1]


        err_w0 = err(w0,s[-1])
        ic(err_w0)
        # err_w0 = 0
        # ic(s[-1])

        if s[-1]>=w0:
            ss[2] = ss[1]
            ss[1] = (ss[0]+ss[1])/2
        else:
            ss[0] = ss[1]
            ss[1] = (ss[1]+ss[2])/2
        ic(s[-1],ss)
        # end = time.time()
        # if end-start>10:
        #     break

    # Initial guess for coefficients (e.g., for a cubic series)
    initial_guess = [1, 1]  # Adjust based on the expected number of coefficients

    # Fit the power series to the data
    coefficients, covariance = curve_fit(power_series, Pc, ds_dt, p0=initial_guess)

    # Generate x values for plotting the fitted curve
    x_fit = np.linspace(min(Pc), max(Pc), 100)
    y_fit = power_series(x_fit, *coefficients)
    plt.plot(x_fit, y_fit, 'b')

    pl(T,s,'Tempo [s]','Regressão [mm]','Regressão em função do tempo')
    pl(Pc/10**6,ds_dt,'Pressão na Câmara [MPa]','Burn Rate [mm/s]','Taxa de regressão em função da pressão')



    return 0




if __name__ == '__main__':
    main()
