# ---------------------------------------------------------------------------
# Datastruktur for en rakett
# ---------------------------------------------------------------------------
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Rocket:
    """Konfigurasjonsparametere for én rakett.

    Parametere
    ----------
    name : str
        Navn på raketten (brukes i plott-legend).
    mass_total : float
        Total masse inkl. motor ved oppskytning [kg].
    diameter : float
        Diameter på rakettens største tverrsnitt [m].
    thrust : float
        Skyvekraft (gjennomsnittlig) fra motoren [N].
    thrust_duration : float
        Brenntid for motoren [s].
    angle_deg : float
        Avfyringsvinkel målt fra horisontalen [grader].
        0° = horisontalt, 90° = rett opp.
    color : str
        Farge for plottlinjen (matplotlib fargenavn).
    parachute_enabled : bool
        True hvis raketten har fallskjerm, False ellers.
    parachute_deploy_time : float
        Tid i sekunder fra motorstans til fallskjerm åpner [s].
    parachute_brake_time : float
        Tid i sekunder fra fallskjerm åpner til raketten har bremsset ned
        til endelig horisontal drifthastighet (wind_speed) [s].
    wind_speed : float
        Endelig horisontal drifthastighet etter bremsing – tilsvarer
        vindhastigheten [m/s].
    """

    name: str
    mass_total: float
    diameter: float
    thrust: float
    thrust_duration: float
    angle_deg: float = 90.0
    color: str = "C0"

    # Fallskjermparametere
    parachute_enabled: bool = False
    parachute_deploy_time: float = 0.0   # sekunder etter motorstans til fallskjerm åpner [s]
    parachute_brake_time: float = 5.0    # sekunder fra fallskjerm åpner til endelig horisontal hastighet [s]
    wind_speed: float = 0.0              # endelig horisontal drifthastighet (vindhastighet) [m/s]

    # Avledet feltene fylles ut av __post_init__
    area: float = field(init=False, repr=False)
    angle_rad: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.area = np.pi * (self.diameter / 2) ** 2
        self.angle_rad = np.radians(self.angle_deg)
