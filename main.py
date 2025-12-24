from startup import *
from motor_library import load_motor, MotorConfig, process_motor_specs
from thrust import calculate_thrust, thrust_pressure_plot
from plots import save_array_to_eng_file


# TODO:
#  1: (SOLVED) Calculation of optimal throat diameter integrated via process_motor_specs.
#  2: (SOLVED) Burnrate.py now handles propellant sub-variants and lacks motor.py dependency.
#  4: Fix log scale graph: ensured plotting handles t > 0 and MPa scaling.
#  5: (SOLVED) process_motor_specs declutters simulation by pre-calculating constants.
#  7: (SOLVED) Added Kn_max vs P_target comparison to validate nozzle sizing.
#  10: (SOLVED) o_ring_thickness added to MotorConfig and accounted for in pressure.py.
#  13: Improve thrust accuracy by replacing the "clip" in thrust.py with Summerfield Criterion.
#  14: Unit Testing: Create a script to verify that "Motor 12" output remains consistent.

def main():
    # 1. Configuration
    # Discretization steps
    N = 10000

    # 2. Load the Motor from the library
    try:
        # Example: motor_12 is a KNSU motor
        motor = load_motor("motor_12")
        # Optional: Set O-ring thickness if separating grains (TODO #10)
        motor.o_ring_thickness = 2.0
        print(f"--- Loaded Motor: {motor.name} ---")
    except ValueError as e:
        print(f"Error loading motor: {e}")
        return

    # 3. Pre-Simulation Analysis (TODO #1, #5, #7)
    # This declutters the main logic by calculating constants first
    specs = process_motor_specs(motor)

    print(f"Propellant:      {motor.prop}")
    print(f"Target Pressure: {motor.P_target} MPa")
    print(f"Ideal Dt:        {specs['dt_ideal']:.2f} mm (for P_target)")
    print(f"Hardware Dt:     {motor.Dt:.2f} mm")

    # Check if the nozzle is properly sized for the requested pressure
    dt_error = abs(motor.Dt - specs['dt_ideal'])
    if dt_error > 0.5:
        print(f"WARNING: Nozzle Dt error is {dt_error:.2f} mm. Expect pressure deviation.")

    # 4. Define Nozzle Efficiency and Expansion Ratio
    # These could eventually move into the MotorConfig class
    eta_noz = 0.95
    Ae_At = 6.278

    # 5. Run the Simulation
    # This calls pressure.py (using O-ring logic) and thrust.py internally
    F, Pc_MPa, t, Cf, It = calculate_thrust(N, motor, eta_noz, Ae_At)

    # 6. Output Results
    print(f"\n--- Simulation Results ---")
    print(f"Peak Pressure:   {max(Pc_MPa):.3f} MPa")
    print(f"Max Thrust:      {max(F):.2f} N")
    print(f"Total Impulse:   {It:.2f} Ns")
    print(f"Burn Time:       {t[-1]:.3f} s")

    # 7. Export to OpenRocket (.eng format)
    # Using the standardized dictionary for export
    info_eng = {
        'filename': f"{motor.name}_simulation",
        'name': motor.name,
        'outer_diameter': str(motor.De),
        'length': str(motor.L * motor.Ng),
        'delay_charge_time': 'P',
        'propellant_mass': f"{(It / 800):.3f}",  # Approximate mass calculation
        'total_mass': f"{(It / 800):.3f}",
        'manufacturer': 'TauRocketTeam'
    }

    # To export, uncomment the line below:
    # save_array_to_eng_file(np.column_stack((t, F)), info_eng, "./")

    # 8. Visualize Results
    # This helper generates the Pressure and Thrust curves
    thrust_pressure_plot(N, motor, Ae_At)

    # Example for TODO #4: Log Scale Plotting
    # ensure we don't have zeros for log scale
    # mask = t > 0
    # plt.figure()
    # plt.loglog(t[mask], Pc_MPa[mask])
    # plt.title("Log-Log Pressure Curve")
    # plt.grid(True, which="both", ls="-")
    # plt.show()


if __name__ == '__main__':
    main()