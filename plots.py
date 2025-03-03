import


def plt_m_grains(N,id_prop,arr_props,motor,eta_noz=0.85,AeAt=6.3):
    for prop in arr_props:
        motor[id_prop] = prop
        F,Pc,t,Cf = calculate_thrust(N,motor,eta_noz,AeAt)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t,Pc)
    plt.grid(True)
    plt.show()

def plt_AeAt(N,arr_aeat,motor,eta_noz=0.85):
    for aeat in arr_aeat:
        F,Pc,t,Cf = calculate_thrust(N,motor,eta_noz,aeat)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t, Cf)
    plt.grid(True)
    plt.show()