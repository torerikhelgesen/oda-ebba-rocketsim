"""
rockets_config.py – Konfigurasjon for rakettsimulator

Definer listen ROCKETS med Rocket-objekter.
Kjør simulatoren med:

    python rocket_sim.py rockets_config.py
"""

from rocket import Rocket

ROCKETS = [
    # -----------------------------------------------------------------------
    # Rakett 1 – 35° fra horisontal, ingen fallskjerm
    # -----------------------------------------------------------------------
    Rocket(
        name="Rakett 1 – 35°",
        mass_total=0.058,      # 58 g total masse inkl. motor
        diameter=0.029,        # 29 mm diameter
        thrust=5.0,            # 5 N skyvekraft
        thrust_duration=1.7,   # 1.7 s brenntid
        angle_deg=35.0,        # 35° fra horisontalen
        color="steelblue",
    ),
    # -----------------------------------------------------------------------
    # Rakett 2 – 45° fra horisontal, ingen fallskjerm
    # -----------------------------------------------------------------------
    Rocket(
        name="Rakett 2 – 45°",
        mass_total=0.058,
        diameter=0.029,
        thrust=5.0,
        thrust_duration=1.7,
        angle_deg=45.0,        # 45° fra horisontalen
        color="darkorange",
    ),
    # -----------------------------------------------------------------------
    # Rakett 3 – 55° fra horisontal, med fallskjerm
    # -----------------------------------------------------------------------
    Rocket(
        name="Rakett 3 – 55° (fallskjerm)",
        mass_total=0.058,
        diameter=0.029,
        thrust=5.0,
        thrust_duration=1.7,
        angle_deg=55.0,        # 55° fra horisontalen
        color="mediumseagreen",
        parachute_enabled=True,
        parachute_deploy_time=2.0,   # 2 s etter motorstans åpner fallskjermen
        parachute_brake_time=3.0,    # 3 s å bremse ned til vindhastighet
        wind_speed=3.0,              # 3 m/s vindhastighet (endelig horisontal drift)
    ),
    # -----------------------------------------------------------------------
    # Rakett 4 – 65° fra horisontal, med fallskjerm
    # -----------------------------------------------------------------------
    Rocket(
        name="Rakett 4 – 65° (fallskjerm)",
        mass_total=0.058,
        diameter=0.029,
        thrust=5.0,
        thrust_duration=1.7,
        angle_deg=65.0,        # 65° fra horisontalen
        color="crimson",
        parachute_enabled=True,
        parachute_deploy_time=2.0,   # 2 s etter motorstans åpner fallskjermen
        parachute_brake_time=3.0,    # 3 s å bremse ned til vindhastighet
        wind_speed=3.0,              # 3 m/s vindhastighet (endelig horisontal drift)
    ),
]
