---
title: Pollutant Build-up and Wash-off
track: storm
level: 1
status: ready
summary: Solids accumulate on a 1 ha parking lot in dry weather and are washed off during 80 days of real summer rainfall. Wash-off depends on the runoff depth, so intense storms after long dry spells carry the highest loads.
plugins: [buildup_washoff, Sewer_system]
features: [Exponential build-up, Depth-dependent wash-off, Immobile surface constituent, Supply-limited loads, Flow-weighted mean concentration]
keywords: [buildup, build-up, washoff, wash-off, first flush, emc, event mean concentration, flow weighted mean concentration, impervious, parking lot, urban runoff, stormwater quality, pollutant loading, tss, total suspended solids, sediment, street dirt, antecedent dry period, kinematic wave, swmm]
components:
  Parking_Lot: "A 10,000 m² impervious lot (100 m wide, 100 m flow length, slope 0.01, Manning's n 0.015) with no depression storage and a runoff coefficient of 1. It holds both the sheet-flow water and the surface solids store. It starts with 0.5 mm of water left over from earlier rain."
  Collection_Tank: An accounting store that receives all runoff and has no outlet. Its storage is the cumulative runoff volume, its TSS mass is the cumulative wash-off load, and its TSS concentration is the running flow-weighted mean concentration of everything that has left the lot.
  Runoff: Kinematic-wave sheet flow from the lot to the tank. Flow is always from the lot to the tank. It carries TSS at the lot's concentration.
  Rain: Hourly rainfall recorded at BWI airport, Maryland, 1 July to 18 September 2010 (`rainfall.txt`), applied over the lot area.
  Buildup: Exponential (saturating) build-up of surface solids, with a rate constant of 0.2 1/day toward a maximum load of 5 g/m².
  Surface_Solids: Solids stored on the pavement (street dirt), in g per m² of surface. They do not move with the water; they only grow by build-up and shrink by wash-off. Starts at 2 g/m².
  TSS: Total suspended solids in the runoff water (g/m³, equal to mg/L). Produced only by wash-off.
  k_w: Wash-off rate coefficient, 5×10⁶ 1/(m²·day). Multiplied by the square of the runoff depth, it gives the fraction of the surface load removed per day.
  Washoff: Release of surface solids into the water at a rate k_w·B·h² per unit area (B is the surface load, h the water depth on the lot).
inputs:
  rainfall.txt: "Rainfall in the three-column precipitation format: interval start (day), interval end (day), rainfall depth in the interval (m). Hourly intervals; day 0 is 1 July 2010; dry hours are omitted. Source: NOAA hourly precipitation record at Baltimore/Washington International Airport (BWI), Maryland, USA (US public domain, 0.01 in = 0.254 mm resolution)."
plots:
  - title: Rainfall and runoff
    ylabel: Flow (m³/day)
    series:
      - {column: "Parking_Lot_Precipitation", label: "Rainfall on the lot"}
      - {column: "Runoff_flow", label: "Runoff"}
    caption: The impervious lot turns nearly all rain into runoff, with a lag and peak smoothing of a few minutes caused by storage in the sheet flow.
  - title: Solids stored on the surface
    ylabel: Surface load B (g/m²)
    series:
      - {column: "Parking_Lot_Surface_Solids:concentration", label: "Surface solids"}
    caption: The load climbs toward 5 g/m² between storms and drops sharply when a storm washes it off. The 20-day dry spell before day 73 brings it almost to saturation.
  - title: Wash-off load rate
    ylabel: TSS load (g/day)
    series:
      - {column: "Runoff_TSS:masstransfer", label: "TSS leaving the lot"}
    caption: The highest load rates come early in intense storms that follow dry weather. Storms that arrive soon after another storm carry little.
  - title: Cumulative flow-weighted mean concentration
    ylabel: TSS (mg/L)
    series:
      - {column: "Collection_Tank_TSS:concentration", label: "Cumulative TSS mass / cumulative runoff volume"}
    caption: Each event pulls the running mean toward its own event mean concentration, upward after dry spells and downward when a large storm falls on a depleted surface.
---

## What this model represents

A paved parking lot of 1 ha drains to a single outlet. Between storms, solids (tire and brake wear, dust, litter fragments, atmospheric deposition) accumulate on the pavement. During a storm, the thin sheet of runoff picks the solids up and carries them off the lot. This build-up / wash-off concept is the standard way to model pollutant loads from impervious urban surfaces, and it underlies the water-quality routines of SWMM and similar models.

The example uses 80 days of real hourly summer rainfall, so it contains short and long dry periods and storms of different sizes. That makes it possible to see the two regimes that control urban stormwater loads:

- **Supply-limited** events, in which the storm is large enough to strip most of the available solids, so the load depends on how much has accumulated since the last storm.
- **Transport-limited** events, in which the storm is too small or too gentle to remove much of what is there.

## How it works

**Runoff.** The lot is a `Catchment` block. Its water storage S (m³) gains rainfall and loses runoff:

  dS/dt = P·A − Q,  h = S/A

where P is the rainfall intensity from `rainfall.txt` (m/day), A = 10,000 m² is the lot area and h is the average water depth (m). The `Runoff` link (`Catchment_link`) computes the outflow with a kinematic-wave (Manning) relation:

  Q = 86400 · (W/n) · S₀^0.5 · (h − d_s)₊^(5/3)  (m³/day)

with width W = 100 m, Manning's n = 0.015, slope S₀ = 0.01 and depression storage d_s = 0. In the most intense hour of the record (about 23 mm/h), the water depth on the lot peaks at about 3.5 mm.

**Build-up.** `Surface_Solids` is an `Immobile_Constituent`: it is stored per unit surface area (B, g/m²) and is never carried by the flow. The `Buildup` source (type `Build up (Saturation)`) adds mass at the rate

  A · k_b · (B_max − B)  (g/day)

so that, per unit area, dB/dt = k_b·(B_max − B). With k_b = 0.2 1/day and B_max = 5 g/m², the surface approaches saturation with a time constant of 5 days: a clean surface reaches 63% of B_max in 5 days and 95% in 15 days. The plugin labels `build_up_rate` in g/day/m², but because it multiplies the difference B_max − B, its actual unit is 1/day.

**Wash-off.** The `Washoff` reaction is a `surface_release` reaction. Its rate is evaluated per unit area,

  r = (k_w · B) · α · h^β  (g/m²/day)

where k_w·B is the concentration-dependence expression, and α = 1 and β = 2 are the release coefficient and depth exponent set on the lot. The reaction removes this mass from `Surface_Solids` (stoichiometric coefficient −1) and adds it to `TSS` in the water (+1), multiplied by the lot area. Wash-off is therefore first order in the surface load, with a rate constant that depends on the runoff depth:

  k(h) = k_w · h²

With k_w = 5×10⁶ 1/(m²·day), k is about 5 1/day at h = 1 mm and about 60 1/day (2.5 1/h) at h = 3.5 mm. Light rain barely disturbs the surface; intense rain strips it within an hour or two.

**Transport.** TSS leaves the lot with the runoff at the lot concentration C (upwind advection, Q·C). The mass balances on the lot are

  d(A·B)/dt = A·k_b·(B_max − B) − A·k_w·B·h²
  d(S·C)/dt = A·k_w·B·h² − Q·C

**Collection tank.** All runoff ends in `Collection_Tank`, a `Catch basin` block (1,000 m² base area) with no outlet. It is not a physical structure. It integrates the outflow, so the results show cumulative runoff volume (m³), cumulative TSS load (g) and their ratio, the flow-weighted mean concentration (mg/L). The wash-off reaction is also defined in the tank, but the tank holds no surface solids, so it has no effect there.

## What to look for in the results

- **Volume check.** The rainfall file contains 215.6 mm. The tank collects 2,160 m³, which equals 215.6 mm on 1 ha plus the 5 m³ of initial water. Runoff is essentially complete because the lot has no losses.
- **Build-up between storms.** The surface load recovers toward 5 g/m² at a decreasing rate. It reaches 4.95 g/m² during the 20-day dry spell between days 52 and 73.
- **Supply-limited storms.** The storm on days 8 to 9 (30 mm) washes off 43 kg and lowers B from 4.5 to 1.0 g/m². The larger storm on days 12 to 13 (about 55 mm of runoff) carries only 17.5 kg, at an event mean concentration of 32 mg/L, because the two earlier storms had already depleted the surface.
- **Antecedent dry period.** The 17 mm storm on day 73, after 20 dry days, produces 38 kg and the highest event mean concentration of the larger storms (227 mg/L).
- **Small storms.** Events of 1 to 4 mm hardly change B. The water depth stays below 1 mm, so k(h) stays below about 5 1/day, and the runoff lasts only a few hours.
- **First flush.** In the larger storms, the runoff TSS concentration peaks within the first hours (250 to 310 mg/L) and then falls while the flow is still high, because the surface load is being exhausted.
- **Period totals.** Over 80 days, about 277 kg of solids leave the lot, at a flow-weighted mean concentration of 128 mg/L. This is within the range commonly reported for parking-lot runoff.

## Assumptions and limitations

- The lot is fully impervious, with no depression storage, infiltration or evaporation. Every millimetre of rain becomes runoff.
- Build-up depends only on the current surface load. It ignores street sweeping, wind removal and seasonal changes. The build-up parameters (k_b, B_max) and the wash-off coefficient k_w are illustrative values; calibrate them against measured event loads before using the model for a real site.
- Wash-off is driven by the water depth on the lot (h²). Other formulations use rainfall intensity or runoff rate per unit area. Raindrop detachment is not represented separately.
- TSS is treated as a single constituent that moves with the water. There is no settling or re-deposition on the lot and no particle-size distribution.
- The lot is one well-mixed storage, so travel-time differences across the lot are not resolved.
- After a storm, the water remaining on the lot drains slowly and keeps the concentration it had at the end of the event. The TSS concentration in this vanishing film has no practical meaning, which is why the plots show load rates and cumulative values.
- The lot starts with 0.5 mm of water (5 m³ of clean water), so the runoff calculation does not start exactly at rest. This has no visible effect on the results.
