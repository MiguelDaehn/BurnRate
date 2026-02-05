from startup import *
from motor_library import load_motor, MotorConfig, process_motor_specs
from thrust import calculate_thrust, thrust_pressure_plot
from plots import plt_m_parameter, plot_log_pressure, save_array_to_eng_file
from reporting import *
import numpy as np
from pathlib import Path  # Add this import at the top if missing
from motor_library import run_full_simulation

def demo_export_openrocket(motor_name="motor_12"):
    """
    TEST 4: Data Export
    - Calculates TRUE length (grains + o-rings).
    - Saves to both local results and OpenRocket directory.
    """
    print(f"\n=== DEMO 4: OpenRocket Export ({motor_name}) ===")
    motor = load_motor(motor_name)
    F, Pc, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)

    # 1. FIX: Calculate True Length (Length of grains + sum of all O-rings)
    # If Ng=1, rings=0. If Ng=2, rings=1.
    # This calculates one O-ring PER grain (Ng)
    total_len = (motor.L * motor.Ng) + (motor.Ng * motor.o_ring_thickness)
    info_eng = {
        'filename': f"{motor.name}_sim",
        'name': f"{motor.name}_Simulated",
        'outer_diameter': str(motor.De),
        'length': f"{total_len:.2f}",  # Uses the corrected length
        'delay_charge_time': 'P',
        'propellant_mass': f"{(It / 1200):.3f}",
        'total_mass': f"{(It / 1000):.3f}",
        'manufacturer': 'TauRocketTeam'
    }

    # 2. FIX: Define Export Paths
    # We want to save to 'results/eng_files' AND the system's OpenRocket folder
    local_path = Path("results/eng_files")

    # Create the list of destinations
    export_destinations = [local_path, path_thrustcurves]

    print(f"Saving {motor.name}_sim.eng to {len(export_destinations)} locations...")

    # 3. Save
    data = np.column_stack((t, F))
    save_array_to_eng_file(data, info_eng, export_destinations)
    print("Export Complete.")


def demo_generate_report(motor_name="motor_12"):
    """
    TEST 6: PDF Report Generation
    Simulates the motor and creates a professional PDF summary.
    """
    print(f"\n=== DEMO 6: Generating PDF Report ({motor_name}) ===")
    motor = load_motor(motor_name)

    # Run Simulation
    F, Pc, t, Cf, It = calculate_thrust(10000, motor, 0.95, 6.278)

    # Generate PDF
    output_filename = f"{motor.name}_Report.pdf"
    create_pdf_report(motor, t, Pc, F, It, filename=output_filename)



def demo_sensitivity_report(motor_name="motor_12",n_analises=5):
    """
    TEST 7: Sensitivity Report Generation
    Compares multiple configurations and saves a summary PDF.
    """
    print(f"\n=== DEMO 7: Sensitivity Analysis Report ({motor_name}) ===")
    motor = load_motor(motor_name)

    # Define what we want to test
    # Example: Varying Grain Lengths to see effect on pressure and impulse
    param = "Dt"
    original_Dt = motor.Dt
    values = np.linspace(motor.Dt*0.9,motor.Dt*1.05,n_analises)
    # values = np.array([7,8,9,10])

    print(f"Varying '{param}' across: {values}")

    # Output path
    filename = os.path.join('./results/reports/', f"{motor.name}_Sensitivity_{param}.pdf")

    # Generates tha thang yo
    create_sensitivity_report(motor, param, values, filename)


# Add to main():
# demo_sensitivity_report("motor_12")


def demo_single_run(motor_name="motor_12"):
    """
    TEST 1: The Basics
    - Loads a motor configuration.
    - Checks if the nozzle is sized correctly for the target pressure.
    - Simulates the burn.
    - Prints performance metrics and plots the standard curves.
    """
    print(f"\n=== DEMO 1: Sta"
          f"ndard Simulation ({motor_name}) ===")

    # 1. Load Motor
    try:
        motor = load_motor(motor_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # 2. Sizing Check (The Pre-processor)
    # This tells you if your hardware (Dt) matches your physics goals (P_target)
    specs = process_motor_specs(motor)
    print(f"Propellant:      {motor.prop}")
    print(f"Target Pressure: {motor.P_target} MPa")
    print(f"Ideal Dt:        {specs['dt_ideal']:.2f} mm")
    print(f"Hardware Dt:     {motor.Dt:.2f} mm")

    if abs(motor.Dt - specs['dt_ideal']) > 0.5:
        print(">> WARNING: Significant Nozzle Dt mismatch! Expect off-target pressure.")

    # 3. Run Simulation
    # N=10000 gives high precision. eta_noz=0.95 is typical for well-made nozzles.
    F, Pc_MPa, t, Cf, It = calculate_thrust(N=10000, motor=motor, eta_noz=0.95, Ae_At=6.278)

    # 4. Results Output
    print("-" * 30)
    print(f"Peak Pressure:   {max(Pc_MPa):.3f} MPa")
    print(f"Max Thrust:      {max(F):.2f} N")
    print(f"Total Impulse:   {It:.2f} Ns")
    print(f"Burn Time:       {t[-1]:.3f} s")
    print("-" * 30)

    # 5. Visualize
    thrust_pressure_plot(10000, motor, Ae_At=6.278)


def demo_parameter_sweeps(motor_name="motor_12"):
    """
    TEST 2: Sensitivity Analysis
    - Demonstrates how changing one parameter (like Throat Diameter or Length)
    - affects the Thrust and Pressure curves.
    - Uses the dynamic 'plt_m_parameter' tool.
    """
    print(f"\n=== DEMO 2: Parameter Sweeps ({motor_name}) ===")
    motor = load_motor(motor_name)

    # Sweep A: Throat Diameter (Dt)
    # We test 90%, 100%, and 110% of the current diameter
    current_dt = motor.Dt
    dt_values = [current_dt * 0.95, current_dt, current_dt * 1.05]

    print(f"Sweeping Dt values: {[round(x, 2) for x in dt_values]} mm...")
    plt_m_parameter(10000, "Dt", dt_values, motor)

    # IMPORTANT: Reset motor attribute because objects are mutable!
    motor.Dt = current_dt

    # Sweep B: Grain Length (L)
    # See how adding length increases pressure (Kn) and burn time
    l_values = [motor.L * 0.9, motor.L, motor.L * 1.1]

    print(f"Sweeping Grain Length values: {[round(x, 2) for x in l_values]} mm...")
    plt_m_parameter(10000, "L", l_values, motor)