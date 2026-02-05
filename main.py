# main.py
from demos import *
from startup import *
from analysis import run_motor_analysis


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