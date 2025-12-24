from startup import *
from motor_library import load_motor, MotorConfig
from thrust import calculate_thrust, thrust_pressure_plot
from plots import save_array_to_eng_file

# TODO:
#  1:
#  Add SRM's calculation of optimal throat diameter for the pressure.
#  3:
#  Correct the error, discontinuity that occurs
#  when pressure drops to 0. just set ds/dt = 0.
#  4:
#  log scale graph not working. is it because the graph is in MPa? shouldn't be, right?
#  5:
#  Add a function that takes initial parameters such as a Diameter
#  And returns ALL needed parameters that can be calculated quickly
#  In order to declutter other functions (having calculations in them that don't serve the main purpose)
#  7:
#  Kn depends on pressure. look at tables to the right of the first page of SRM
#  Kn of a certain pressure (our desired MEOP) is calculated. Kn = Ab/At -> At = Kn_max * Ab_max
#  8:
#  There's an error when you try to run plt_AeAt(N, array_AeAt, motor, eta_noz=0.85):
#  It seems that for some reason the thrust is getting multiplied, like 3000 N when it was supposed to be ~500
#  Ok apparently it surges when the expansion ratio goes above 9 or 10
#  9:
#  YOU NEED TO FIX THE CF (THRUST COEFFICIENT) SOONER RATHER THAN LATER THIS IS A SERIOUS ISSUE
#  10:
#  Add functionality to check if the user is separating KNSB grains with o-rings
#  12: make it so that 'motor' and 'grain' are significantly separate, with different classes




def main():
    # 1. Configuration and Discretization
    # High N for precision, lower N for quick iterations
    N = 10000

    # 2. Load the Motor from the library
    # Replaces: motor = mot(12)
    try:
        motor = load_motor("motor_12")
        print(f"--- Simulating Motor: {motor.name} ---")
    except ValueError as e:
        print(e)
        return

    # 3. Define Nozzle and Environment Parameters
    eta_noz = 0.95
    Ae_At = 6.278  # Expansion ratio

    # 4. Run the Simulation
    # This calls pressure.py and thrust.py internally using the new objects
    F, Pc_MPa, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)

    # 5. Output Results
    print(f"Simulation Results for {motor.name}:")
    print(f"  - Peak Pressure: {max(Pc_MPa):.3f} MPa")
    print(f"  - Max Thrust:    {max(F):.2f} N")
    print(f"  - Total Impulse: {It:.2f} Ns")
    print(f"  - Burn Time:     {t[-1]:.3f} s")

    # 6. Export to OpenRocket (.eng format)
    # Re-using your existing logic but with the new objects
    info_eng = {
        'filename': f"{motor.name}_sim",
        'name': motor.name,
        'outer_diameter': str(motor.De),
        'length': str(motor.L),
        'delay_charge_time': 'P',
        'propellant_mass': f"{(max(F) / 100):.3f}",  # Example calc
        'total_mass': f"{(max(F) / 100):.3f}",
        'manufacturer': 'TauRocketTeam'
    }

    data_export = np.column_stack((t, F))
    # Ensure path_thrustcurves is defined in startup.py or locally
    # save_array_to_eng_file(data_export, info_eng, "./")

    # 7. Visualize
    thrust_pressure_plot(N, motor, Ae_At)


if __name__ == '__main__':
    main()