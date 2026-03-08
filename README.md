# Rakettsimulator for Oda og Ebba

> **Et fysikkprosjekt** – simulering av modelrakettbaner med luftmotstand, tyngdekraft og motorskyvekraft.

---

## Innholdsfortegnelse

1. [Om programmet](#om-programmet)
2. [Installasjon og kjøring](#installasjon-og-kjøring)
3. [Konfigurasjon av raketter](#konfigurasjon-av-raketter)
4. [Fysikk og formler](#fysikk-og-formler)
   - [Koordinatsystem](#koordinatsystem)
   - [Krefter som virker på raketten](#krefter-som-virker-på-raketten)
   - [Tyngdekraft](#tyngdekraft)
   - [Skyvekraft](#skyvekraft)
   - [Luftmotstand](#luftmotstand)
   - [Nesekonens betydning](#nesekonens-betydning)
   - [Lufttetthet som funksjon av høyde](#lufttetthet-som-funksjon-av-høyde)
   - [Masse](#masse)
   - [Bevegelsesligningene](#bevegelsesligningene)
   - [Numerisk integrasjon – Runge-Kutta 4. orden (RK4)](#numerisk-integrasjon--runge-kutta-4-orden-rk4)
5. [Plottene som produseres](#plottene-som-produseres)
6. [Eksempel på resultater](#eksempel-på-resultater)
7. [Filstruktur](#filstruktur)

---

## Om programmet

Programmet `rocket_sim.py` simulerer flybanen til én eller flere modelraketter i én og samme kjøring. Det tar hensyn til:

- **Tyngdekraft** (konstant *g* = 9,81 m/s²)
- **Motorskyvekraft** i en angitt brennperiode
- **Luftmotstand** beregnet med en realistisk luftmotstandskoeffisient for raketter med ogivnese
- **Varierende lufttetthet** med høyden (barometrisk formel)
- **Drivstofforbruk** som reduserer massen under brennfasen

Simulatoren bruker **4. ordens Runge-Kutta (RK4)** for presis numerisk integrasjon av bevegelsesligningene.

---

## Installasjon og kjøring

### Krav

- Python 3.9 eller nyere
- `numpy`
- `matplotlib`

### Installer avhengigheter

```bash
pip install numpy matplotlib
```

### Kjør med standardkonfigurasjon

Programmet inneholder tre ferdigdefinerte eksempelraketter:

```bash
python rocket_sim.py
```

### Kjør med egendefinert konfigurasjonsfil

```bash
python rocket_sim.py rockets_config.py
```

Etter kjøring skrives resultater til terminalen og plottet lagres som `rakett_simulering.png`.

---

## Konfigurasjon av raketter

Rakettkonfigurasjonen beskrives med `Rocket`-klassen. Enten bruker du standard-listen i `rocket_sim.py` (`DEFAULT_ROCKETS`), eller du lager en egen fil som `rockets_config.py` med en liste kalt `ROCKETS`.

### Parametere for en rakett

| Parameter | Type | Enhet | Beskrivelse |
|---|---|---|---|
| `name` | `str` | – | Navn på raketten (vises i plott) |
| `mass_total` | `float` | kg | Total masse ved oppskytning inkl. motor |
| `diameter` | `float` | m | Ytterdiameter på raketten |
| `thrust` | `float` | N | Gjennomsnittlig motorskyvekraft |
| `thrust_duration` | `float` | s | Brenntid for motoren |
| `angle_deg` | `float` | grader | Avfyringsvinkel fra horisontalen (0° = horisontalt, 90° = rett opp) |
| `color` | `str` | – | Farge på plottkurven (matplotlib-fargenavn) |

### Eksempel på konfigurasjonsfil

```python
from rocket_sim import Rocket

ROCKETS = [
    Rocket(
        name="Min rakett",
        mass_total=0.058,      # 58 g total masse inkl. motor
        diameter=0.029,        # 29 mm
        thrust=5.0,            # 5 N
        thrust_duration=1.7,   # 1.7 s
        angle_deg=45.0,        # 45° fra horisontalen
        color="royalblue",
    ),
]
```

---

## Fysikk og formler

### Koordinatsystem

Vi bruker et todimensjonalt koordinatsystem:

- **x-akse** – horisontal retning (positiv i skyteretningens horisontale komponent)
- **y-akse** – vertikal retning (positiv oppover)

Raketten skytes ut fra origo `(0, 0)` med en vinkel `θ` (theta) målt fra horisontalen.

```
y ↑
  |      /  ← rakettbane
  |     /
  |    /  θ ← vinkel fra horisontalen
  |___/________→ x
```

---

### Krefter som virker på raketten

Tre krefter virker til enhver tid:

```
F_netto = F_skyv + F_drag + F_tyngde
```

Hver kraft dekomponeres i x- og y-komponenter og Newton 2. lov brukes:

```
a = F_netto / m
```

---

### Tyngdekraft

Tyngdekraften virker alltid rett ned:

```
F_g = m · g
```

- `m` = aktuell masse [kg]
- `g` = 9,81 m/s²

I vektorform: `F_g = (0, −m·g)`

---

### Skyvekraft

Motoren brenner i `t_burn` sekunder og produserer en skyvekraft `F_T` langs den innledende skyteretningen:

```
F_Tx = F_T · cos(θ)     (horisontal komponent)
F_Ty = F_T · sin(θ)     (vertikal komponent)
```

For `t > t_burn`:  `F_Tx = F_Ty = 0`

I virkeligheten varierer skyvekraften over tid (se motorens thrustcurve). Her bruker vi en konstant gjennomsnittsverdi, som er en god tilnærming for enkle beregninger.

---

### Luftmotstand

Luftmotstandskraften på et legeme som beveger seg gjennom luft er:

```
F_drag = ½ · ρ(h) · v² · C_d · A
```

| Symbol | Beskrivelse | Typisk verdi |
|---|---|---|
| `ρ(h)` | Lufttetthet ved høyde `h` [kg/m³] | 1,225 ved havnivå |
| `v` | Fart (absolutt hastighet) [m/s] | – |
| `C_d` | Luftmotstandskoeffisient (dimensjonsløs) | 0,35 (ogivnese) |
| `A` | Frontareal (tverrsnittareal) [m²] | `π·(d/2)²` |

Luftmotstanden virker **motsatt av hastighetsretningen**:

```
F_drag_x = −F_drag · (vx / v)
F_drag_y = −F_drag · (vy / v)
```

---

### Nesekonens betydning

Formen på nesekonen påvirker `C_d`-verdien sterkt. En raketts nesekone er designet for å minimere luftmotstand. De vanligste formene er:

| Neseform | Typisk C_d | Merknad |
|---|---|---|
| Flat plate (bunn) | ~1,1 | Høyest motstand |
| Kjegle (conical) | ~0,50 | Enkel å lage |
| **Ogiv (tangent ogive)** | **~0,35** | God kompromiss, brukt i dette programmet |
| Von Kármán (Haack series) | ~0,25 | Matematisk optimal for subsoniske hastigheter |
| Paraboloid | ~0,30 | Vanlig i kommersielle raketter |

Programmet bruker `C_d = 0,35`, som tilsvarer en typisk **ogivnese** – den neseformen som oftest brukes i modelraketter. Ogiven er en sirkelbuekurve som gir en glatt overgang og minimal trykkdrag.

```
     /\         ← Spiss topp
    /  \
   /    \       ← Ogiv-profil (sirkelbuekurve)
  |      |
  |      |      ← Sylindrisk kropp
  |      |
```

---

### Lufttetthet som funksjon av høyde

Lufttettheten avtar med høyden etter den **barometriske formel** (isoterm atmosfære):

```
ρ(h) = ρ₀ · exp(−h / H)
```

| Symbol | Verdi | Beskrivelse |
|---|---|---|
| `ρ₀` | 1,225 kg/m³ | Lufttetthet ved havnivå |
| `H` | 8500 m | Skalahøyde (scale height) |
| `h` | – | Høyde over bakken [m] |

For modelraketter (maks 1–3 km) er effekten liten (ca. 10–30 % redusert tetthet), men den er inkludert for realisme.

**Eksempel:**
- ved `h = 0 m`:  `ρ = 1,225 kg/m³`
- ved `h = 500 m`: `ρ ≈ 1,155 kg/m³` (−5,7 %)
- ved `h = 1000 m`: `ρ ≈ 1,089 kg/m³` (−11 %)

---

### Masse

Massen er konstant gjennom hele flukten og er lik `mass_total` – total masse inkl. motor ved oppskytning:

```
m(t) = m_total     (konstant)
```

Denne forenklingen er god for typiske modelraketter der motormassen er liten i forhold til totalvekten.

---

### Bevegelsesligningene

Tilstandsvektoren er `[x, y, vx, vy]`. De deriverte er:

```
dx/dt  = vx
dy/dt  = vy
dvx/dt = (F_Tx + F_drag_x) / m(t)
dvy/dt = (F_Ty + F_drag_y − m(t)·g) / m(t)
```

Dette er et koplede ordinære differensialligningssystem (ODE) som løses numerisk.

---

### Numerisk integrasjon – Runge-Kutta 4. orden (RK4)

Programmet bruker **Runge-Kutta 4. orden** for å integrere bevegelsesligningene fremover i tid. RK4 er vesentlig mer nøyaktig enn enkel Euler-integrasjon fordi den evaluerer deriverte fire ganger per tidssteg og veier dem optimalt.

For et generelt problem `dy/dt = f(t, y)` beregnes neste steg slik:

```
k1 = f(t,           y)
k2 = f(t + h/2,     y + h·k1/2)
k3 = f(t + h/2,     y + h·k2/2)
k4 = f(t + h,       y + h·k3)

y(t + h) = y(t) + (h/6) · (k1 + 2·k2 + 2·k3 + k4)
```

- `h` = tidssteg (standard: 0,01 s = 10 ms)
- Globalfeil er av orden `O(h⁴)` – svært liten ved `h = 0,01 s`

RK4 er standardmetoden for fysikksimuleringer der nøyaktighet er viktigere enn beregningshastighet.

---

## Plottene som produseres

Programmet produserer tre plott side om side:

| Plott | X-akse | Y-akse | Beskrivelse |
|---|---|---|---|
| **Bane** | Horisontal avstand [m] | Høyde [m] | Den faktiske flybanen i rommet |
| **Høyde over tid** | Tid [s] | Høyde [m] | Viser oppstigning og nedstigning |
| **Horisontal hastighet** | Tid [s] | Horisontal hastighet [m/s] | Viser akselerasjon og luftmotstandsdemping |

For **baneplottet** markeres landingspunktet med en pil (▼).

I legenden for baneplottet vises:
- `h_max` – maksimal høyde oppnådd
- `d` – horisontal rekkevidde ved landing

---

## Eksempel på resultater

Kjøring med `rockets_config.py` (fire raketter):

| Rakett | Masse | Skyvekraft | Vinkel | Maks høyde | Rekkevidde | Flygetid |
|---|---|---|---|---|---|---|
| Rakett 1 | 58 g | 5 N | 35° | 144 m | 585 m | 11,6 s |
| Rakett 2 | 58 g | 5 N | 45° | 210 m | 571 m | 13,8 s |
| Rakett 3 | 58 g | 5 N | 55° | 272 m | 513 m | 15,7 s |
| Rakett 4 | 58 g | 5 N | 65° | 326 m | 414 m | 17,2 s |

---

## Filstruktur

```
oda-ebba-rocketsim/
├── rocket_sim.py       # Hovedprogrammet med simuleringsmotor og standardkonfig
├── rockets_config.py   # Eksempel på ekstern konfigurasjonsfil
└── README.md           # Denne filen
```
