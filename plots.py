from thrust import *


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
    '''Plots both Thrust (F) and Thrust Coefficient (CF) as a function of time'''
    for aeat in arr_aeat:
        F,Pc,t,Cf = calculate_thrust(N,motor,eta_noz,aeat)
        plt.figure(1)
        plt.plot(t,F)
        plt.figure(2)
        plt.plot(t, Cf)
    plt.grid(True)
    plt.show()


def save_array_to_eng_file(data, motor_info,path):
    filename, name, outer_diameter, length, delay_charge_time, propellant_mass, total_mass,manufacturer = motor_info.values()
    """
    Saves a 2D numpy array with 2 columns to a .eng file with a custom header.

    Parameters:
    - data: A numpy array with 2 columns and many rows.
    - filename: The name of the file (without extension).
    - name: The name of the data (e.g., 'My_Engine_01').
    - outer_diameter: Motor outer diameter.
    - length: Motor length.
    - delay_charge_time: Delay charge time.
    - propellant_mass: Propellant mass.
    - total_mass: Total mass (propellant+dry weight -> if you want to manually add the parts' weight).
                  and location, propellant_mass == total_mass
    - manufacturer: Manufacturer name.
    """

    # Ensure the filename ends with .eng
    if not filename.endswith('.eng'):
        filename += '.eng'

    # Create the header string
    header = f"{name} {outer_diameter} {length} {delay_charge_time} {propellant_mass} {total_mass} {manufacturer}"

    # Save the array to the file with the header
    np.savetxt(path+filename, data, fmt='%.6f', delimiter='\t', header=header, comments='')





def main():

    return 0

if __name__ == '__main__':
    main()