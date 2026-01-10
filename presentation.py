import os
import numpy as np
import matplotlib.pyplot as plt

# --- IMPORTS ---
from motor_library import load_motor, process_motor_specs
from thrust import calculate_thrust, thrust_pressure_plot
from plots import plt_m_parameter, save_array_to_eng_file
# Importing the star feature
from burnrate import BR_from_pressure


def print_header(title):
    """Helper to make the console output look like a presentation slide header."""
    print("\n" + "=" * 60)
    print(f" {title.upper()}")
    print("=" * 60)


def pause_for_effect():
    """Pauses execution until the presenter is ready."""
    input("\n[Press ENTER to continue to the next demo phase...]")


def run_presentation():
    # Configuration
    MOTOR_ID = "motor_12"
    # We use a real test file from your 'data' folder for the regression demo
    TEST_DATA_ID = "pressao_teste_30_05"

    print_header("SRM SIMULATOR: JUNIOR TRAINING DEMO")
    print(f"Target Motor: {MOTOR_ID}")
    print("Objective:    From Raw Data -> Characterization -> Sim -> Report")

    # ---------------------------------------------------------
    # PHASE 0: SETUP
    # ---------------------------------------------------------
    print("Loading motor configuration...")
    try:
        motor = load_motor(MOTOR_ID)
        print(f"✅ Loaded '{motor.name}' (Propellant: {motor.prop})")
    except ValueError as e:
        print(f"❌ Error loading motor: {e}")
        return

    pause_for_effect()

    # ---------------------------------------------------------
    # PHASE 1: PROPELLANT CHARACTERIZATION (THE CORE FEATURE)
    # ---------------------------------------------------------
    print_header("Phase 1: Burn Rate Characterization")
    print(f"Goal: Derive Saint-Robert's coefficients (a, n) from experimental data.")
    print(f"Input Data: 'data/BR_{TEST_DATA_ID}.csv'")

    # Temporarily widen pressure limits to ensure we capture all test data points
    original_p_max = motor.p_max
    motor.p_max = 20.0

    print("Running regression algorithm...")
    try:
        # This function returns the pressure arrays and the fitted parameters
        Pc_data, BR_data, params = BR_from_pressure(TEST_DATA_ID, motor)
        a, n = params[0], params[1]

        print("\n--- RESULTS ---")
        print(f"✅ Regression Successful!")
        print(f"   Pre-exponential factor (a): {a:.5f}")
        print(f"   Pressure Exponent (n):      {n:.5f}")
        print(f"   Derived Law: r = {a:.4f} * P^{n:.4f}")

        # Plotting the regression (Visual Proof)
        print("\nDisplaying Regression Plot...")
        plt.figure(figsize=(8, 5))
        plt.scatter(Pc_data, BR_data, color='black', alpha=0.6, s=15, label='Experimental Data')

        # Generate smooth line for the fit
        p_space = np.linspace(min(Pc_data), max(Pc_data), 100)
        br_fit = a * (p_space ** n)
        plt.plot(p_space, br_fit, color='red', linewidth=2, label=f'Fit: r={a:.3f}P^{n:.3f}')

        plt.title(f"Burn Rate Characterization: {motor.prop}")
        plt.xlabel("Chamber Pressure [MPa]")
        plt.ylabel("Burn Rate [mm/s]")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    except Exception as e:
        print(f"⚠️  Skipping regression demo due to data error: {e}")

    # Restore motor state
    motor.p_max = original_p_max
    pause_for_effect()

    # ---------------------------------------------------------
    # PHASE 2: VALIDATION CHECK
    # ---------------------------------------------------------
    print_header("Phase 2: Geometry & Physics Check")
    specs = process_motor_specs(motor)

    dt_error = abs(motor.Dt - specs['dt_ideal'])
    print(f"   - Target Pressure: {motor.P_target} MPa")
    print(f"   - Ideal Throat Dt: {specs['dt_ideal']:.3f} mm")
    print(f"   - Actual Hardware: {motor.Dt:.3f} mm")

    if dt_error > 0.5:
        print(f"⚠️  WARNING: Mismatch of {dt_error:.2f}mm. Pressure will deviate.")
    else:
        print("✅ Geometry is optimized for target pressure.")

    pause_for_effect()

    # ---------------------------------------------------------
    # PHASE 3: NUMERICAL SIMULATION
    # ---------------------------------------------------------
    print_header("Phase 3: Full Motor Simulation")
    print("Solving internal ballistics (Steps=10,000)...")

    F, Pc, t, Cf, It = calculate_thrust(10000, motor, eta_noz=0.95, Ae_At=6.278)

    print("\nSimulation Complete. KPIs:")
    print(f"   🚀 Peak Thrust:    {max(F):.2f} N")
    print(f"   🔥 Peak Pressure:  {max(Pc):.3f} MPa")
    print(f"   ⏱️  Burn Time:      {t[-1]:.3f} s")
    print(f"   📈 Total Impulse:  {It:.2f} Ns")

    print("\nVisualizing Thrust & Pressure curves...")
    thrust_pressure_plot(10000, motor, Ae_At=6.278)

    # ---------------------------------------------------------
    # PHASE 4: SENSITIVITY ANALYSIS
    # ---------------------------------------------------------
    print_header("Phase 4: Sensitivity (Safety Check)")
    print("Scenario: Manufacturing tolerance check (+/- 10% on Throat Dt).")

    original_dt = motor.Dt
    variations = [original_dt * 0.9, original_dt, original_dt * 1.1]

    print(f"Sweeping Dt: {[round(v, 2) for v in variations]} mm")
    plt_m_parameter(10000, "Dt", variations, motor)

    motor.Dt = original_dt  # Reset
    pause_for_effect()

    # ---------------------------------------------------------
    # PHASE 5: DELIVERABLES
    # ---------------------------------------------------------
    print_header("Phase 5: Generating Deliverables")

    # 1. OpenRocket
    print("1. Exporting OpenRocket (.eng) file...")
    data_matrix = np.column_stack((t, F))
    header_info = {
        'filename': f"{motor.name}_sim",
        'name': f"{motor.name}_Simulated",
        'outer_diameter': str(motor.De),
        'length': str(motor.L * motor.Ng),
        'delay_charge_time': 'P',
        'propellant_mass': f"{(It / 1200):.3f}",
        'total_mass': f"{(It / 1000):.3f}",
        'manufacturer': 'TauRocketTeam'
    }
    # Using the path fix we implemented earlier
    save_array_to_eng_file(data_matrix, header_info, path="./results/eng_files/")

    # 2. PDF Report
    print("\n2. Compiling PDF Report...")
    try:
        # Lazy import to avoid 'Agg' backend blocking previous plots
        from reporting import create_pdf_report
        report_name = f"{motor.name}_Presentation_Report.pdf"
        create_pdf_report(motor, t, Pc, F, It, filename=report_name)
    except Exception as e:
        print(f"Report generation skipped: {e}")

    print("\n" + "=" * 60)
    print(" DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_presentation()