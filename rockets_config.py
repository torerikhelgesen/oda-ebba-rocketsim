"""
rockets_config.py – Eksempelkonfigurasjon for rakettsimulator

Definer listen ROCKETS med Rocket-objekter.
Kjør simulatoren med:

    python rocket_sim.py rockets_config.py
"""

from rocket_sim import Rocket

ROCKETS = [
    # -----------------------------------------------------------------------
    # Klassisk liten hobbyrakett, rett opp
    # -----------------------------------------------------------------------
    Rocket(
        name="Mini-Alfa – Rett opp",
        mass_total=0.100,      # 100 g total masse
        diameter=0.029,        # 29 mm diameter
        thrust=10.0,           # 10 N skyvekraft
        thrust_duration=1.0,   # 1 s brenntid
        angle_deg=0.0,         # rett opp
        fuel_mass=0.015,       # 15 g drivstoff
        color="steelblue",
    ),
    # -----------------------------------------------------------------------
    # Mellomklasse rakett med 15° vinkel
    # -----------------------------------------------------------------------
    Rocket(
        name="Midt-Beta – 15° vinkel",
        mass_total=0.180,      # 180 g
        diameter=0.032,        # 32 mm
        thrust=20.0,           # 20 N
        thrust_duration=1.8,   # 1.8 s
        angle_deg=15.0,        # 15° fra vertikalen
        fuel_mass=0.025,       # 25 g
        color="darkorange",
    ),
    # -----------------------------------------------------------------------
    # Større rakett med kraftig motor og høy vinkel
    # -----------------------------------------------------------------------
    Rocket(
        name="Stor-Gamma – 30° vinkel",
        mass_total=0.300,      # 300 g
        diameter=0.040,        # 40 mm
        thrust=45.0,           # 45 N
        thrust_duration=2.5,   # 2.5 s
        angle_deg=30.0,        # 30° fra vertikalen
        fuel_mass=0.060,       # 60 g
        color="mediumseagreen",
    ),
]
