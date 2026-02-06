# main.py
from demos import *
from startup import *
from analysis import run_motor_analysis
from EzImpulse import design_dual_mission_system

def main():
    """
    Main Entry Point.
    Uncomment the function you want to run.
    """
    print("--- SRM Simulator Ready ---")
    mot_1 = "Hadron_07"
    mot_2 = "Quark3_07"

    run_motor_analysis(mot_1, auto_size=True)
    run_motor_analysis(mot_2, auto_size=True)

    design_dual_mission_system(
        alt_target_a_m=600,
        dry_mass_a_kg=3.073,

        alt_target_b_m=1200,
        dry_mass_b_kg=3.500,

        cd=0.5,
        airframe_dia_mm=2.5 * 25.4,
        motor_od_mm=56,
        motor_core_mm=25,
        propellant='knsb'
    )



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