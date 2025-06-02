import numpy as np
from dataclasses import dataclass
from typing import Dict
from startup import *
from burnrate import pp
import matplotlib.pyplot as plt


@dataclass
class Nozzle:
    Dt: float  # Throat diameter (mm)
    De: float  # Exit diameter (mm)
    efficiency: float = 0.85

    @property
    def At(self) -> float:
        return np.pi * (self.Dt / 2) ** 2

    @property
    def Ae(self) -> float:
        return np.pi * (self.De / 2) ** 2

    @property
    def Ae_At(self) -> float:
        return self.Ae / self.At


@dataclass
class Propellant:
    name: str
    rho_ideal: float
    k: float
    molecular_weight: float
    T0: float
    a: float
    n: float

    @classmethod
    def from_name(cls, prop_name: str):
        base_name = prop_name.split('_')[0]
        dp = dict_prop.get(base_name.lower(), 2)
        try:
            burn_data = pp(base_name)[0]  # Get first pressure range data
            a, n = burn_data[2], burn_data[3]
        except:
            a, n = 5.0, 0.5  # Fallback values

        return cls(
            name=prop_name,
            rho_ideal=properties_table[0][dp],
            k=properties_table[1][dp],
            molecular_weight=properties_table[2][dp],
            T0=properties_table[3][dp],
            a=a,
            n=n
        )


@dataclass
class GrainGeometry:
    De: float
    Di: float
    L: float
    Ng: int
    csi: bool = False
    esi: bool = False
    osi: bool = True

    @property
    def web_thickness(self) -> float:
        return (self.De - self.Di) / 2

    def burn_area(self, web: float) -> float:
        burned_Di = self.Di + (2 * web * (not self.csi))
        burned_De = self.De - (2 * web * (not self.osi))
        burned_L = self.L - (2 * web * (not self.esi))
        return (
                (np.pi / 4) * (burned_De ** 2 - burned_Di ** 2) * 2 * self.Ng * (not self.esi) +
                np.pi * burned_De * burned_L * self.Ng * (not self.osi) +
                np.pi * burned_Di * burned_L * self.Ng * (not self.csi)
        )


class RocketMotor:
    def __init__(self, propellant: Propellant, geometry: GrainGeometry, nozzle: Nozzle, rho_pct: float):
        self.propellant = propellant
        self.geometry = geometry
        self.nozzle = nozzle
        self.rho_pct = rho_pct
        self.rho_g = rho_pct * propellant.rho_ideal * 1000  # kg/m³ → g/mm³
        self.cstar = np.sqrt((Ru / propellant.molecular_weight) * propellant.T0 / propellant.k *
                             ((propellant.k + 1) / 2) ** ((propellant.k + 1) / (propellant.k - 1)))

    def simulate(self, N: int = 1000) -> Dict[str, np.ndarray]:
        web = np.linspace(0, self.geometry.web_thickness, N)
        results = {
            'time': np.zeros(N),
            'pressure': np.zeros(N),
            'thrust': np.zeros(N),
            'burn_rate': np.zeros(N),
            'web': web
        }

        # Initial conditions
        results['pressure'][0] = patm
        results['burn_rate'][0] = self.propellant.burn_rate(patm)

        for i in range(1, N):
            # Calculate burn rate in mm/s
            results['burn_rate'][i] = self.propellant.burn_rate(results['pressure'][i - 1])

            # Time increment in seconds
            dt = (web[i] - web[i - 1]) / results['burn_rate'][i] if results['burn_rate'][i] > 0 else 0
            results['time'][i] = results['time'][i - 1] + dt

            # Calculate chamber pressure in MPa
            Ab = self.geometry.burn_area(web[i])
            mdot_prop = Ab * results['burn_rate'][i] * self.rho_g  # g/s
            Pc_pa = (mdot_prop / 1000 * self.cstar / (self.nozzle.At / 1e6)) ** (1 / (1 + self.propellant.n))
            results['pressure'][i] = Pc_pa * 1e-6  # Convert to MPa

            # Calculate thrust in N
            results['thrust'][i] = self._calculate_thrust(results['pressure'][i])

        return results

    def _calculate_thrust(self, Pc_MPa: float) -> float:
        Pc_Pa = Pc_MPa * 1e6
        Me = find_M2(self.nozzle.Ae_At, self.propellant.k)
        P2 = Pc_Pa / (1 + (self.propellant.k - 1) / 2 * Me ** 2) ** (self.propellant.k / (self.propellant.k - 1))

        cf = (eta_noz * np.sqrt(2 * self.propellant.k ** 2 / (self.propellant.k - 1) *
                               (2 / (self.propellant.k + 1)) ** ((self.propellant.k + 1) / (self.propellant.k - 1)) *
                               (1 - (P2 / Pc_Pa) ** ((self.propellant.k - 1) / self.propellant.k))) +
              (P2 - patm_pa) / Pc_Pa * (self.nozzle.Ae_At))

        return (self.nozzle.At / 1e6) * cf * Pc_Pa


# Example usage with proper motor parameters
if __name__ == "__main__":
    # Create components for a KNSU motor
    propellant = Propellant.from_name("knsu")
    nozzle = Nozzle(Dt=12.54, De=23.6)  # ~3.54 expansion ratio
    geometry = GrainGeometry(
        De=48.34, Di=17.44, L=64.1, Ng=2,  # L = average of 44.74 and 83.46
        csi=False, esi=False, osi=False
    )

    # Create and simulate motor
    motor = RocketMotor(
        propellant=propellant,
        geometry=geometry,
        nozzle=nozzle,
        rho_pct=0.89
    )
    results = motor.simulate(N=500)

    # Plot results with proper scaling
    plt.figure(figsize=(12, 8))

    plt.subplot(311)
    plt.plot(results['time'], results['pressure'])
    plt.ylabel('Pressure (MPa)')
    plt.grid(True)

    plt.subplot(312)
    plt.plot(results['time'], results['thrust'])
    plt.ylabel('Thrust (N)')
    plt.grid(True)

    plt.subplot(313)
    plt.plot(results['time'], results['burn_rate'])
    plt.ylabel('Burn Rate (mm/s)')
    plt.xlabel('Time (s)')
    plt.grid(True)

    plt.tight_layout()
    plt.show()