from startup import *



def Ab_f(N,De,Di0,L,s):
    A_b = pi*N*(0.5*(De**2-(Di0+2*s)**2)+(L-2*s)*(Di0+2*s))
    return A_b


def Delta_s(At,Ab,Pc,rho,cstar,delta_t):
    delta_s = (At*Pc*delta_t)/(Ab*rho*cstar)
    return delta_s

def BR_from_pressure(id,motor_data):
    T, Pc = LoadData('BR', id.lower(), 'csv')
    Pc = Pc * 10 ** 6
    delta_t = np.array([T[i + 1] - T[i] for i in range(len(T) - 1)])
    delta_t = np.append(delta_t, delta_t[-1])
    dt_avg = np.average(delta_t)


    prop = motor_data[0].lower()
    Dt = motor_data[1].astype(float)
    rho_pct = motor_data[2].astype(float)
    Ng = motor_data[3].astype(int)
    L = motor_data[4].astype(float)
    De = motor_data[5].astype(float)
    Di = motor_data[6].astype(float)
    w0 = (De-Di)/2
    rho_g = rho_pct*rho_prop[prop]

    At = pi*(Dt/2)**2
    Vg = pi*((De/2/10)**2-(Di/2/10)**2)*(L/10)
    mp = Ng * Vg * rho_g
    Psum = np.sum(Pc)
    cstar = ((At / mp) * Psum * dt_avg) / 1000
    err_w0 = 1.0

    Ab = np.zeros_like(T)
    s = np.zeros_like(T)
    delta_s = np.zeros_like(T)
    ds_dt = np.zeros_like(T)

    delta_s[1] = 0.1
    ss = np.array([0, 5, 100]) / 100
    while err_w0 > 1e-15:
        s[1] = ss[1]
        for i, t in enumerate(T):

            Ab[i] = Ab_f(Ng, De, Di, L, s[i - 1])
            # ic(Ab[i])
            if i > 1:
                s[i] = s[i - 1] + delta_s[i - 1]
            if i > 0:
                delta_s[i] = Delta_s(At, Ab[i], Pc[i], rho_g, cstar, delta_t[i])
                ds_dt[i] = delta_s[i] / delta_t[i]

        err_w0 = err(w0, s[-1])
        # ic(err_w0)

        if s[-1] >= w0:
            ss[2] = ss[1]
            ss[1] = (ss[0] + ss[1]) / 2
        else:
            ss[0] = ss[1]
            ss[1] = (ss[1] + ss[2]) / 2

    return Pc/10**6,ds_dt





def main():
    return 0

if __name__ == '__main__':
    main()
