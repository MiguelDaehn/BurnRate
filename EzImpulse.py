import numpy as np
from scipy.optimize import brentq

# --- PHYSICS CONSTANTS ---
G0 = 9.80665
MAX_IT = 5_000.0
MIN_IT = 0.1
TOLERANCE = 0.05

# Standard properties (Density in g/cm^3)
# Based on your uploaded Hadron data sheet
PROPELLANT_DATA = {
    'kndx': {'rho': 1.879, 'isp_est': 125},
    'knsb': {'rho': 1.841, 'isp_est': 120},
    'knsu': {'rho': 1.889, 'isp_est': 130},
    'kner': {'rho': 1.820, 'isp_est': 120},
    'knfr': {'rho': 1.942, 'isp_est': 125},
    'knpsb': {'rho': 1.923, 'isp_est': 125},
}


def suggest_motor_configurations(target_impulse_ns: float,
                                 De_mm: float,
                                 Di_mm: float,
                                 prop_name: str,
                                 density_eff: float = 0.95,
                                 custom_isp: float = None):
    """
    Calculates grain geometry options to achieve a target impulse.
    """
    # 1. Get Propellant Properties
    prop_key = prop_name.lower()
    if prop_key not in PROPELLANT_DATA:
        print(f"❌ Unknown propellant '{prop_name}'. Available: {list(PROPELLANT_DATA.keys())}")
        return

    prop_data = PROPELLANT_DATA[prop_key]
    rho_ideal_g_cm3 = prop_data['rho']

    # Use custom Isp if provided, otherwise use estimate
    isp = custom_isp if custom_isp else prop_data['isp_est']

    # 2. Calculate Required Mass
    # It = m * Isp * g0  ->  m = It / (Isp * g0)
    req_mass_kg = target_impulse_ns / (isp * G0)

    # 3. Calculate Required Volume
    # rho_effective = rho_ideal * efficiency
    # V = m / rho
    rho_eff_kg_m3 = (rho_ideal_g_cm3 * 1000) * density_eff
    req_vol_m3 = req_mass_kg / rho_eff_kg_m3

    # 4. Geometric Constraints
    # Area of the annulus (cross-section)
    area_m2 = (np.pi / 4) * ((De_mm / 1000) ** 2 - (Di_mm / 1000) ** 2)

    # Total length of propellant required (if it were one long stick)
    total_length_m = req_vol_m3 / area_m2
    total_length_mm = total_length_m * 1000

    # 5. Output Report
    print(f"\n📐 Motor Sizing Report for {target_impulse_ns:.1f} Ns ({prop_name.upper()})")
    print(f"   Target Isp: {isp} s | Density Eff: {density_eff * 100:.0f}%")
    print(f"   Required Propellant Mass: {req_mass_kg * 1000:.1f} g")
    print(f"   Grain Geometry: OD={De_mm}mm, ID={Di_mm}mm")
    print(f"   Total Length Needed: {total_length_mm:.1f} mm\n")

    print(f"   {'Ng':<4} | {'L_grain (mm)':<15} | {'Aspect Ratio (L/D)':<20} | {'Notes'}")
    print("   " + "-" * 60)

    # 6. Generate Options (1 to 6 grains)
    for ng in range(1, 7):
        l_grain = total_length_mm / ng
        aspect_ratio = l_grain / De_mm

        # Heuristic for "Good" BATES grains:
        # Neutral burn is typically around L = 1.5 * De to 2.0 * De
        note = ""
        if 1.5 <= aspect_ratio <= 2.2:
            note = "✅ Ideal BATES"
        elif 1.0 <= aspect_ratio < 1.5:
            note = "⚠️ Slightly Progressive"
        elif aspect_ratio > 2.5:
            note = "⚠️ Regressive / Long"
        elif aspect_ratio < 0.8:
            note = "❌ Too short (Sliver)"

        print(f"   {ng:<4} | {l_grain:<15.1f} | {aspect_ratio:<20.2f} | {note}")
    print("\n")



def get_air_density(altitude_m):
    """
    Standard Atmosphere Model (Troposphere up to 11km).
    rho = 1.225 * (1 - h / 44330)^4.256
    """
    if altitude_m < 0: altitude_m = 0
    if altitude_m > 11000: return 0.364  # Simplified Stratosphere floor

    # Temperature lapse rate model
    T0 = 288.15
    L = 0.0065
    T = T0 - L * altitude_m
    pressure = 101325 * (1 - L * altitude_m / T0) ** 5.25577
    density = pressure / (287.05 * T)
    return density


def simulate_apogee_1d(impulse_ns, dry_mass_kg, cd, diameter_mm, isp_s, avg_thrust_n=None):
    """
    Runs a fast 1D vertical flight simulation to find apogee.

    Args:
        impulse_ns: Total Impulse (The variable we are solving for)
        dry_mass_kg: Rocket mass without fuel
        avg_thrust_n: Estimated Average Thrust. If None, assumes a
                      typical high-performance T/W ratio of 10.
    """
    # 1. Derive Propellant Mass (The "Inverse" part)
    # It = mp * Isp * g0  =>  mp = It / (Isp * g0)
    propellant_mass = impulse_ns / (isp_s * G0)

    # 2. Estimate Burn Time
    # If we don't know thrust, we assume a "snappy" motor (10G accel)
    # to minimize gravity losses, which is typical for sizing.
    initial_mass = dry_mass_kg + propellant_mass
    if avg_thrust_n is None:
        avg_thrust_n = initial_mass * G0 * 10
        # Clamp min thrust to avoid div/0 or unrealistic long burns
        avg_thrust_n = max(avg_thrust_n, 10.0)

    burn_time = impulse_ns / avg_thrust_n

    # 3. Integration Loop
    t = 0
    y = 0  # Altitude
    v = 0  # Velocity
    m = initial_mass
    dt = 0.01  # Time step (coarse is fine for sizing)

    area = np.pi * (diameter_mm / 1000 / 2) ** 2

    # Fly until Apogee (v < 0)
    while v >= 0 or t < burn_time:
        # Stop if we crash
        if y < 0 and t > 0.1: return 0

        # Stop if we are falling (Apogee reached)
        if v < 0 and t > burn_time: break

        # --- PHYSICS ---
        rho = get_air_density(y)
        drag = 0.5 * rho * v ** 2 * cd * area
        gravity = m * G0

        if t < burn_time:
            thrust = avg_thrust_n
            dm = propellant_mass / burn_time
            m -= dm * dt
        else:
            thrust = 0
            m = dry_mass_kg  # Empty

        # F = ma
        acc = (thrust - drag - gravity) / m

        # Euler Integration
        v += acc * dt
        y += v * dt
        t += dt

    return y


def solve_required_impulse(target_alt_m, dry_mass_kg, cd, diameter_mm, isp_s=130,avg_thrust_n=None):
    """
    Finds the Total Impulse (Ns) required to hit a specific altitude.
    Uses Brent's Method to root-find the error between Sim_Apogee and Target.
    """
    print(f"🎯 Mission Planning: Target {target_alt_m}m with {dry_mass_kg}kg Dry Mass...")

    # Error Function: f(It) = Sim_Apogee(It) - Target
    def error_func(it_guess):
        if it_guess < 1: return -target_alt_m
        apogee = simulate_apogee_1d(it_guess, dry_mass_kg, cd, diameter_mm, isp_s,avg_thrust_n)
        return apogee - target_alt_m

    # Solve
    # Search range: 10 Ns (Tiny) to 50,000 Ns (Huge, O-class)
    try:
        required_it = brentq(error_func, MIN_IT, MAX_IT, xtol=1.0)
    except ValueError:
        print("❌ Could not converge. Target likely impossible with given parameters.")
        return None

    # Calculate final stats for the user
    prop_mass = required_it / (isp_s * G0)
    print(f"✅ Solution Found:")
    print(f"   Required Impulse: {required_it:.2f} Ns")
    print(f"   Propellant Mass:  {prop_mass * 1000:.1f} g (Est.)")
    print(f"   Est. Motor Class: {get_motor_class(required_it)}")

    return required_it


def get_motor_class(impulse):
    # Quick helper for classification
    classes = "ABCDEFGHIJKLM"
    limits = [2.5 * (2 ** i) for i in range(13)]  # 2.5, 5, 10, 20...
    for i, limit in enumerate(limits):
        if impulse <= limit:
            return classes[i]
    return "N+"


def design_single_grain(target_impulse_ns: float,
                        De_mm: float,
                        Di_mm: float,
                        prop_name: str,
                        density_eff: float = 0.95):
    """
    Calculates the exact Grain Length required to achieve a SINGLE target impulse
    for different grain counts (Ng = 1 to 8).

    Args:
        target_impulse_ns: The mission goal (Ns)
        De_mm: Grain Outer Diameter
        Di_mm: Grain Inner Diameter
        prop_name: Propellant string (e.g. 'knsu')
    """
    # 1. Get Propellant Data
    prop_key = prop_name.lower()
    if prop_key not in PROPELLANT_DATA:
        print(f"❌ Unknown propellant '{prop_name}'")
        return

    rho_ideal = PROPELLANT_DATA[prop_key]['rho']
    isp = PROPELLANT_DATA[prop_key]['isp_est']
    rho_eff_kg_m3 = (rho_ideal * 1000) * density_eff

    # 2. Calculate Total Required Volume
    # Mass = It / (Isp * g0)
    m_total_kg = target_impulse_ns / (isp * G0)

    # Volume = Mass / Density
    vol_total_m3 = m_total_kg / rho_eff_kg_m3

    # Area of Cross Section
    area_m2 = (np.pi / 4) * ((De_mm / 1000) ** 2 - (Di_mm / 1000) ** 2)

    # Total Length needed (if it were one giant stick)
    L_total_mm = (vol_total_m3 / area_m2) * 1000

    # 3. Output Table
    print(f"\n🎯 Single Target Solver")
    print(f"   Target: {target_impulse_ns:.0f} Ns ({prop_name.upper()})")
    print(f"   Geometry: OD={De_mm}mm, ID={Di_mm}mm")
    print(f"   Total Propellant Mass: {m_total_kg * 1000:.1f} g")
    print("   " + "-" * 60)
    print(f"   {'Ng':<5} | {'L_grain (mm)':<15} | {'Ratio (L/D)':<15} | {'Status'}")
    print("   " + "-" * 60)

    # 4. Iterate Options
    for ng in range(1, 9):
        l_grain = L_total_mm / ng
        aspect = l_grain / De_mm

        # Classification
        status = ""
        if 1.5 <= aspect <= 2.0:
            status = "✅ Ideal (BATES)"
        elif 1.0 <= aspect < 1.5:
            status = "⚠️ Progressive"
        elif aspect > 2.5:
            status = "⚠️ Regressive (Long)"
        elif aspect < 0.8:
            status = "❌ Too Short"

        print(f"   {ng:<5} | {l_grain:<15.1f} | {aspect:<15.2f} | {status}")
    print("\n")


def design_modular_grain(target_1_ns: float,
                         target_2_ns: float,
                         De_mm: float,
                         Di_mm: float,
                         prop_name: str,
                         density_eff: float = 0.95,
                         tolerance: float = TOLERANCE):
    """
    Finds a SINGLE grain geometry (Length) that can fulfill TWO different
    impulse targets simply by changing the number of grains (Ng).

    Args:
        target_1_ns: First impulse goal (e.g., 800 Ns for test)
        target_2_ns: Second impulse goal (e.g., 2000 Ns for flight)
        De_mm: Grain Outer Diameter (Constraint)
        Di_mm: Grain Inner Diameter (Constraint)
        tolerance: Acceptable deviation from target impulse (0.10 = 10%)
    """
    # 1. Sort targets so A is smaller, B is larger
    targets = sorted([target_1_ns, target_2_ns])
    It_A, It_B = targets[0], targets[1]

    # 2. Get Propellant Data
    prop_key = prop_name.lower()
    if prop_key not in PROPELLANT_DATA:
        print(f"❌ Unknown propellant '{prop_name}'")
        return

    rho_ideal = PROPELLANT_DATA[prop_key]['rho']
    isp = PROPELLANT_DATA[prop_key]['isp_est']
    rho_eff_kg_m3 = (rho_ideal * 1000) * density_eff

    print(f"\n🧩 Modular Grain Solver")
    print(f"   Targets: {It_A:.0f} Ns  &  {It_B:.0f} Ns")
    print(f"   Geometry: OD={De_mm}mm, ID={Di_mm}mm ({prop_name.upper()})")
    print(f"   Searching for integer combinations (Ng)...")
    print("   " + "-" * 65)
    print(f"   {'Config':<15} | {'L_grain':<10} | {'Ratio (L/D)':<12} | {'Error A':<8} | {'Error B':<8}")

    found_solution = False

    # 3. Iterate through possible integer pairs (e.g., 1:2, 2:3, 3:5)
    # We limit max grains to 8 for practicality
    for n_a in range(1, 6):
        for n_b in range(n_a + 1, 9):

            # Calculate the required "Per-Grain Impulse" for each case
            I_grain_req_A = It_A / n_a
            I_grain_req_B = It_B / n_b

            # Check if these two requirements are close to each other
            # (i.e., can a single grain size satisfy both?)
            avg_I_grain = (I_grain_req_A + I_grain_req_B) / 2

            diff_A = abs(avg_I_grain - I_grain_req_A) / I_grain_req_A
            diff_B = abs(avg_I_grain - I_grain_req_B) / I_grain_req_B

            if diff_A <= tolerance and diff_B <= tolerance:
                found_solution = True

                # 4. Calculate Geometry for this Average Impulse
                # Mass = I / (Isp * g0)
                m_grain_kg = avg_I_grain / (isp * G0)

                # Volume = Mass / Density
                vol_grain_m3 = m_grain_kg / rho_eff_kg_m3

                # Length = Volume / Area
                area_m2 = (np.pi / 4) * ((De_mm / 1000) ** 2 - (Di_mm / 1000) ** 2)
                l_grain_mm = (vol_grain_m3 / area_m2) * 1000

                aspect = l_grain_mm / De_mm

                # 5. Format Output
                # actual impulses achieved
                It_act_A = avg_I_grain * n_a
                It_act_B = avg_I_grain * n_b

                err_str_A = f"{(It_act_A - It_A) / It_A * 100:+.1f}%"
                err_str_B = f"{(It_act_B - It_B) / It_B * 100:+.1f}%"

                row = f"Ng = {n_a} & {n_b}"

                # Quality Check marker
                marker = ""
                if 1.5 <= aspect <= 2.0:
                    marker = "✅ (BATES)"
                elif aspect > 2.5:
                    marker = "⚠️ (Long)"
                elif aspect < 1.0:
                    marker = "⚠️ (Short)"

                print(
                    f"   {row:<15} | {l_grain_mm:<10.1f} | {aspect:<12.2f} | {err_str_A:<8} | {err_str_B:<8} {marker}")
                print(f"     -> Result: {It_act_A:.0f} Ns (Target {It_A}) and {It_act_B:.0f} Ns (Target {It_B})")

    if not found_solution:
        print(f"\n❌ No common grain geometry found within {tolerance * 100}% tolerance.")
        print("   Try changing De/Di dimensions or relaxing the tolerance.")

def design_dual_mission_system(
        # --- Mission A (e.g., Test Flight) ---
        alt_target_a_m: float,
        dry_mass_a_kg: float,

        # --- Mission B (e.g., Competition Flight) ---
        alt_target_b_m: float,
        dry_mass_b_kg: float,

        # --- Shared Vehicle Parameters (Optional: split these too if totally different rockets) ---
        cd: float,
        airframe_dia_mm: float,

        # --- Motor Parameters (Constraints) ---
        motor_od_mm: float,
        motor_core_mm: float,
        propellant: str,
        isp_estimate: float = 110
):
    """
    Full pipeline:
    1. Determines required Impulse for two different rockets/missions.
    2. Synthesizes a single grain geometry that fits both by changing stacking (Ng).
    """
    print(f"🚀 === DUAL MISSION OPTIMIZER === 🚀")
    print(f"   Mission A: {alt_target_a_m}m (Dry Mass: {dry_mass_a_kg} kg)")
    print(f"   Mission B: {alt_target_b_m}m (Dry Mass: {dry_mass_b_kg} kg)")
    print(f"   Motor Constraint: OD={motor_od_mm}mm, Core={motor_core_mm}mm ({propellant})")

    # --- STEP 1: SOLVE FOR IMPULSE A ---
    print(f"\n1️⃣  Analyzing Mission A ({alt_target_a_m}m)...")
    impulse_a = solve_required_impulse(
        target_alt_m=alt_target_a_m,
        dry_mass_kg=dry_mass_a_kg,
        cd=cd,
        diameter_mm=airframe_dia_mm,
        isp_s=isp_estimate
    )

    # --- STEP 2: SOLVE FOR IMPULSE B ---
    print(f"\n2️⃣  Analyzing Mission B ({alt_target_b_m}m)...")
    impulse_b = solve_required_impulse(
        target_alt_m=alt_target_b_m,
        dry_mass_kg=dry_mass_b_kg,
        cd=cd,
        diameter_mm=airframe_dia_mm,
        isp_s=isp_estimate
    )

    if not impulse_a or not impulse_b:
        print("\n❌ Critical Failure: Could not calculate required impulse for one or both missions.")
        return

    # --- STEP 3: FIND COMMON GEOMETRY ---
    print(f"\n3️⃣  Synthesizing Modular Grain Geometry...")
    print(f"    Searching for a common grain segment for {impulse_a:.0f} Ns and {impulse_b:.0f} Ns...")

    impulse_a = round(impulse_a, 1)
    impulse_b = round(impulse_b, 1)

    design_modular_grain(
        target_1_ns=impulse_a,
        target_2_ns=impulse_b,
        De_mm=motor_od_mm,
        Di_mm=motor_core_mm,
        prop_name=propellant
    )


# --- DEMO BLOCK ---
if __name__ == "__main__":
    # Example: Quark Rocket (Estimated Params)

    # solve_required_impulse(
    #     target_alt_m=600,  # 1 km target
    #     dry_mass_kg=3.573,  # Airframe mass
    #     cd=0.5,  # Drag Coeff
    #     diameter_mm=25.4*2.5,  # 56mm airframe
    #     isp_s=100,  # KNSU typical
    #     avg_thrust_n = 286
    # )

    # suggest_motor_configurations(
    #     target_impulse_ns=490,
    #     De_mm=56,  # Fits in 56mm casing
    #     Di_mm=25,  # Core size
    #     prop_name='knsb',
    #     density_eff=0.95
    # )

    # design_modular_grain(
    #     target_1_ns=430,
    #     target_2_ns=760,
    #     De_mm=56,
    #     Di_mm=25,
    #     prop_name='knsb'
    # )

    # design_single_grain(
    #     target_impulse_ns=800,
    #     De_mm=56,
    #     Di_mm=25,
    #     prop_name='knsb'
    # )

    design_dual_mission_system(
        alt_target_a_m=600,
        dry_mass_a_kg=3.073,

        alt_target_b_m=1200,
        dry_mass_b_kg=3.500,

        cd=0.5,
        airframe_dia_mm=2.5*25.4,
        motor_od_mm=56,
        motor_core_mm=25,
        propellant='knsb'
    )