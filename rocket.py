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
    """

    name: str
    mass_total: float
    diameter: float
    thrust: float
    thrust_duration: float
    angle_deg: float = 90.0
    color: str = "C0"

    # Avledet feltene fylles ut av __post_init__
    area: float = field(init=False, repr=False)
    angle_rad: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.area = np.pi * (self.diameter / 2) ** 2
        self.angle_rad = np.radians(self.angle_deg)
