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


def save_array_to_eng_file(data, filename):
    """
    Saves a 2D numpy array with 2 columns to a .eng file.

    Parameters:
    - data: A numpy array with 2 columns and 'n' rows.
    - filename: The name of the file (without extension).
    """
    # Ensure the filename ends with .eng
    if not filename.endswith('.eng'):
        filename += '.eng'

    # Save the array to the file
    np.savetxt(filename, data, fmt='%.6f', delimiter='\t')


# Example usage:
data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])  # Example 2D array
save_array_to_eng_file(data, 'output')  # Saves to 'output.eng'



def main():

    return 0

if __name__ == '__main__':
    main()