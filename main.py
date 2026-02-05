from startup import *
from motor_library import load_motor, MotorConfig, process_motor_specs
from thrust import calculate_thrust, thrust_pressure_plot
from plots import plt_m_parameter, plot_log_pressure, save_array_to_eng_file
from reporting import *
import numpy as np
from pathlib import Path  # Add this import at the top if missing
from motor_library import run_full_simulation
from demonstrations import *
# ==========================================
#        SRM SIMULATOR - TESTING AREA
# ==========================================


def main():
    """
    Uncomment the function you want to run.
    """
    print("--- SRM Simulator Ready ---")
    mot_1 = "Hadron"
    mot_2 = "Quark3"
    MOT = mot_2

    run_full_simulation(MOT, auto_size_throat=False)

    # [1] STANDARD RUN
    # The default workhorse. Check stats and standard plots.
    # demo_single_run(MOT)

    # [2] SENSITIVITY ANALYSIS
    # Compare different geometries side-by-side.
    # demo_parameter_sweeps(MOT)

    # CREATE PDF REPORT FOR MULTIPLE CONFIGURATIONS
    # demo_sensitivity_report(MOT,n_analises=10)


    # OUTDATED FUNCTIONS BELOW ----//--/----//--/----//--/----//--/----//--/----//--/----//--/----//--/----//--/----//
    # [3] EXPORT
    # Generate files for flight simulation.
    # demo_export_openrocket(MOT)
    # CREATE PDF REPORT
    # demo_generate_report(MOT)


if __name__ == '__main__':
    main()