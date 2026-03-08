"""
rocket_sim.py – Simulator for modelraketter

Simulerer banen til en eller flere modelraketter og produserer
tre plott:
  1. Bane (høyde vs. horisontal avstand)
  2. Høyde som funksjon av tid
  3. Horisontal hastighet som funksjon av tid

Bruk:
  python rocket_sim.py                  # kjør med standardkonfigurasjon
  python rocket_sim.py rockets_config.py # kjør med ekstern konfigurasjon
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from typing import List

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------------------------------------------------------
# Fysiske konstanter
# ---------------------------------------------------------------------------
G = 9.81          # tyngdeakselerasjon [m/s²]
RHO_0 = 1.225     # lufttetthet ved havnivå [kg/m³]
H_SCALE = 8500    # skalahøyde for barometrisk formel [m]

# Luftmotstandskoeffisient for typisk ogivnose (lav motstand)
CD = 0.35


# ---------------------------------------------------------------------------
# Datastruktur for en rakett
# ---------------------------------------------------------------------------
@dataclass
class Rocket:
    """Konfigurasjonsparametere for én rakett.

    Parametere
    ----------
    name : str
        Navn på raketten (brukes i plott-legend).
    mass_total : float
        Total masse inkl. drivstoff ved oppskytning [kg].
    diameter : float
        Diameter på rakettens største tverrsnitt [m].
    thrust : float
        Skyvekraft (gjennomsnittlig) fra motoren [N].
    thrust_duration : float
        Brenntid for motoren [s].
    angle_deg : float
        Avfyringsvinkel målt fra vertikalen [grader].
        0° = rett opp, 30° = 30° fra loddlinjen.
    fuel_mass : float
        Masse av drivstoffet som forbrennes [kg].
        Standard 0 (massekonstant simulering).
    color : str
        Farge for plottlinjen (matplotlib fargenavn).
    """

    name: str
    mass_total: float
    diameter: float
    thrust: float
    thrust_duration: float
    angle_deg: float = 0.0
    fuel_mass: float = 0.0
    color: str = "C0"

    # Avledet feltene fylles ut av __post_init__
    area: float = field(init=False, repr=False)
    angle_rad: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.area = np.pi * (self.diameter / 2) ** 2
        self.angle_rad = np.radians(self.angle_deg)


# ---------------------------------------------------------------------------
# Hjelpefunksjoner
# ---------------------------------------------------------------------------
def air_density(altitude: float) -> float:
    """Beregn lufttetthet ved gitt høyde med barometrisk formel.

    rho(h) = rho_0 * exp(-h / H_scale)
    """
    return RHO_0 * np.exp(-max(altitude, 0.0) / H_SCALE)


def _derivatives(state: np.ndarray, t: float, rocket: Rocket) -> np.ndarray:
    """Returner tilstandsderiverte [vx, vy, ax, ay] for RK4.

    Tilstand: [x, y, vx, vy]
    """
    x, y, vx, vy = state

    # --- Aktuell masse ---
    if t < rocket.thrust_duration and rocket.fuel_mass > 0.0:
        burn_rate = rocket.fuel_mass / rocket.thrust_duration
        mass = rocket.mass_total - burn_rate * t
        mass = max(mass, rocket.mass_total - rocket.fuel_mass)
    else:
        mass = rocket.mass_total - rocket.fuel_mass

    # --- Skyvekraft (langs innledende skyteretning) ---
    if t < rocket.thrust_duration:
        Ftx = rocket.thrust * np.sin(rocket.angle_rad)
        Fty = rocket.thrust * np.cos(rocket.angle_rad)
    else:
        Ftx = Fty = 0.0

    # --- Luftmotstand ---
    v = np.hypot(vx, vy)
    rho = air_density(y)
    Fd = 0.5 * rho * v ** 2 * CD * rocket.area
    if v > 1e-9:
        Fdx = -Fd * vx / v
        Fdy = -Fd * vy / v
    else:
        Fdx = Fdy = 0.0

    # --- Tyngdekraft ---
    Fgy = -mass * G

    # --- Netto akselerasjon ---
    ax = (Ftx + Fdx) / mass
    ay = (Fty + Fdy + Fgy) / mass

    return np.array([vx, vy, ax, ay])


def simulate(
    rocket: Rocket, dt: float = 0.01, max_time: float = 600.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simuler rakettbane med 4. ordens Runge-Kutta.

    Returner
    --------
    t  : tidsvektor [s]
    x  : horisontal posisjon [m]
    y  : høyde [m]
    vx : horisontal hastighet [m/s]
    vy : vertikal hastighet [m/s]
    """
    state = np.array([0.0, 0.0, 0.0, 0.0])
    t = 0.0

    results = [[t, state[0], state[1], state[2], state[3]]]

    while t < max_time:
        # RK4
        k1 = _derivatives(state, t, rocket)
        k2 = _derivatives(state + 0.5 * dt * k1, t + 0.5 * dt, rocket)
        k3 = _derivatives(state + 0.5 * dt * k2, t + 0.5 * dt, rocket)
        k4 = _derivatives(state + dt * k3, t + dt, rocket)

        state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt

        results.append([t, state[0], state[1], state[2], state[3]])

        # Stopp når raketten treffer bakken etter at den var i luften
        if state[1] < 0.0 and t > 0.5:
            break

    data = np.array(results)
    return data[:, 0], data[:, 1], data[:, 2], data[:, 3], data[:, 4]


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_results(rockets: List[Rocket], results: list) -> None:
    """Lag tre plott for alle simulerte raketter."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Rakettsimulator – resultater", fontsize=14, fontweight="bold")

    ax_traj, ax_alt, ax_hspd = axes

    # --- Plott 1: Bane (høyde vs. horisontal avstand) ---
    ax_traj.set_title("Bane")
    ax_traj.set_xlabel("Horisontal avstand [m]")
    ax_traj.set_ylabel("Høyde [m]")
    ax_traj.grid(True, linestyle="--", alpha=0.5)

    # --- Plott 2: Høyde vs. tid ---
    ax_alt.set_title("Høyde over tid")
    ax_alt.set_xlabel("Tid [s]")
    ax_alt.set_ylabel("Høyde [m]")
    ax_alt.grid(True, linestyle="--", alpha=0.5)

    # --- Plott 3: Horisontal hastighet vs. tid ---
    ax_hspd.set_title("Horisontal hastighet over tid")
    ax_hspd.set_xlabel("Tid [s]")
    ax_hspd.set_ylabel("Horisontal hastighet [m/s]")
    ax_hspd.grid(True, linestyle="--", alpha=0.5)

    for rocket, (t, x, y, vx, vy) in zip(rockets, results):
        # Klipper bort eventuelle negative høyder i sluttfasen
        mask = y >= 0
        label = rocket.name

        # Legg til statistikk i etiketten
        max_alt = y.max()
        max_range = x[mask].max() if mask.any() else 0.0
        label = f"{rocket.name}\n(h_max={max_alt:.0f} m, d={max_range:.0f} m)"

        if mask.any():
            ax_traj.plot(x[mask], y[mask], color=rocket.color, label=label)
            ax_traj.plot(x[mask][-1], 0, "v", color=rocket.color, markersize=8)  # landingspunkt
        else:
            ax_traj.plot([], [], color=rocket.color, label=label)

        ax_alt.plot(t[mask], y[mask], color=rocket.color, label=rocket.name)

        ax_hspd.plot(t[mask], np.abs(vx[mask]), color=rocket.color, label=rocket.name)

    for ax in axes:
        ax.legend(fontsize=8, loc="upper right")

    plt.tight_layout()
    plt.savefig("rakett_simulering.png", dpi=150, bbox_inches="tight")
    print("Plott lagret som 'rakett_simulering.png'")
    plt.show()


# ---------------------------------------------------------------------------
# Standardkonfigurasjon (brukes hvis ingen ekstern konfig er oppgitt)
# ---------------------------------------------------------------------------
DEFAULT_ROCKETS: List[Rocket] = [
    Rocket(
        name="Rakett A – Rett opp",
        mass_total=0.150,      # 150 g
        diameter=0.030,        # 30 mm
        thrust=15.0,           # 15 N
        thrust_duration=1.5,   # 1.5 s
        angle_deg=0.0,
        fuel_mass=0.020,       # 20 g drivstoff
        color="royalblue",
    ),
    Rocket(
        name="Rakett B – 20° vinkel",
        mass_total=0.150,
        diameter=0.030,
        thrust=15.0,
        thrust_duration=1.5,
        angle_deg=20.0,
        fuel_mass=0.020,
        color="tomato",
    ),
    Rocket(
        name="Rakett C – Kraftigere motor",
        mass_total=0.200,      # 200 g
        diameter=0.035,        # 35 mm
        thrust=30.0,           # 30 N
        thrust_duration=2.0,
        angle_deg=0.0,
        fuel_mass=0.040,
        color="seagreen",
    ),
]


# ---------------------------------------------------------------------------
# Hovedprogram
# ---------------------------------------------------------------------------
def load_rockets_from_module(path: str) -> List[Rocket]:
    """Last raketter fra en ekstern Python-konfigurasjonsfil."""
    spec = importlib.util.spec_from_file_location("rockets_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "ROCKETS"):
        raise AttributeError(
            f"Konfigurasjonsfilen '{path}' mangler variabelen 'ROCKETS'. "
            "Den skal være en liste av Rocket-objekter, f.eks.:\n"
            "  from rocket_sim import Rocket\n"
            "  ROCKETS = [Rocket(name='Min rakett', mass_total=0.15, diameter=0.029, "
            "thrust=12.0, thrust_duration=1.2)]"
        )
    return module.ROCKETS


def main() -> None:
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        print(f"Laster konfigurasjon fra '{config_path}' ...")
        rockets = load_rockets_from_module(config_path)
    else:
        print("Bruker standardkonfigurasjon (tre eksempelraketter) ...")
        rockets = DEFAULT_ROCKETS

    print(f"\nSimulerer {len(rockets)} rakett(er) ...\n")

    results = []
    for rocket in rockets:
        print(f"  {rocket.name}")
        print(f"    Masse total:       {rocket.mass_total*1000:.0f} g")
        print(f"    Diameter:          {rocket.diameter*1000:.0f} mm")
        print(f"    Skyvekraft:        {rocket.thrust:.1f} N")
        print(f"    Brenntid:          {rocket.thrust_duration:.2f} s")
        print(f"    Avfyringsvinkel:   {rocket.angle_deg:.1f}°")
        print(f"    Tverrsnittareal:   {rocket.area*1e4:.2f} cm²")

        t, x, y, vx, vy = simulate(rocket)
        results.append((t, x, y, vx, vy))

        mask = y >= 0
        max_alt = y.max()
        flight_time = t[mask][-1]
        max_range = x[mask].max()
        max_vx = np.abs(vx[mask]).max()
        max_vy = vy.max()

        print(f"    → Maks høyde:      {max_alt:.1f} m")
        print(f"    → Maks rekkevidde: {max_range:.1f} m")
        print(f"    → Flygetid:        {flight_time:.2f} s")
        print(f"    → Maks horisontal hastighet: {max_vx:.1f} m/s")
        print(f"    → Maks vertikal hastighet:   {max_vy:.1f} m/s")
        print()

    plot_results(rockets, results)


if __name__ == "__main__":
    main()
