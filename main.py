from startup import *
from motor_library import load_motor, MotorConfig, process_motor_specs
from thrust import calculate_thrust, thrust_pressure_plot
from plots import plt_m_parameter, plot_log_pressure, save_array_to_eng_file
from reporting import *
import numpy as np
from demos import *
from analysis import *
# ==========================================
#        SRM SIMULATOR - TESTING AREA
# ==========================================




def main():
    """
    Main Entry Point.
    Uncomment the function you want to run.
    """
    print("--- SRM Simulator Ready ---")
    mot_1 = "motor_hadron_04"
    mot_2 = "motor_quark3_04"
    MOT = mot_2

    run_motor_analysis(MOT)
    # [1] STANDARD RUN
    # The default workhorse. Check stats and standard plots.
    # demo_single_run(mot_2)

    # [2] SENSITIVITY ANALYSIS
    # Compare different geometries side-by-side.
    # demo_parameter_sweeps(mot)


    # [3] EXPORT
    # Generate files for flight simulation.
    # demo_export_openrocket(mot_2)

    # CREATE PDF REPORT
    # demo_generate_report(mot_2)

    # CREATE PDF REPORT FOR MULTIPLE CONFIGURATIONS
    # demo_sensitivity_report(mot,n_analises=10)


if __name__ == '__main__':
    main()