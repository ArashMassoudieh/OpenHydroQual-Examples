---
title: Infiltration Basin
track: storm
level: 2
status: ready
summary: A 400 m² infiltration basin receives runoff from 1 ha of pavement and returns it to the aquifer through a 3 m unsaturated zone. Ten soil layers show wetting fronts moving down after each storm, and the largest storm fills the basin to overflow and saturates the whole profile.
plugins: [Pond_Plugin, unsaturated_soil]
features: [Pond-to-soil infiltration, Vadose zone profile, Wetting fronts, Groundwater recharge, Overflow, Drawdown time]
keywords: [infiltration basin, recharge basin, recharge, groundwater recharge, exfiltration, infiltration, lid, gsi, bmp, scm, stormwater control measure, vadose zone, unsaturated zone, wetting front, richards equation, van genuchten, drawdown, managed aquifer recharge, mar, overflow]
components:
  Paved_Catchment: "A 10,000 m² impervious drainage area (100 m wide, slope 0.01, Manning's n 0.015) with no losses."
  Basin: "The infiltration basin: a prism with a flat 400 m² floor at elevation 0 m. Receives runoff and the rain that falls on it. Empty at the start."
  Downstream_Swale: Fixed-head boundary that receives the overflow. Its storage only accumulates the overflow volume.
  Soil: "Ten 0.3 m layers of sandy loam (K_sat 1.06 m/day, θ_s 0.41, θ_r 0.065, α 7.5 1/m, n 1.89), from the basin floor (0 m) down to the water table (−3 m). Vadose_01 is at the top, Vadose_10 at the bottom. All start at a water content of 0.15."
  Water_Table: Groundwater, a fixed head at −3 m, the bottom of the soil column. It receives the recharge.
  Runoff: Kinematic-wave sheet flow from the paved area into the basin. Always positive (into the basin).
  Overflow: "Overflow weir 2 m long from the basin to the swale, crest 1.0 m above the basin floor: Q = 293,760·(H − 1.0)^1.5 m³/day (C = 1.7 m^0.5/s)."
  Infiltration: Flow from the basin into the top soil layer. Positive downward.
  soil_to_soil_link: Unsaturated Darcy flow between adjacent soil layers. Positive downward.
  Recharge: "Flow from the bottom soil layer to the water table. Positive downward; it is slightly negative (capillary rise) early in the run, while the bottom layer is drier than the water table supports."
  Rain: Hourly rainfall at BWI airport, Maryland, 1 August to 11 October 2010, applied to the paved area and the basin.
inputs:
  rainfall.txt: "Rainfall in the three-column precipitation format: interval start (day), interval end (day), rainfall depth in the interval (m). Hourly intervals; day 0 is 1 August 2010; dry hours are omitted. Source: NOAA hourly precipitation record at Baltimore/Washington International Airport (BWI), Maryland, USA (US public domain, 0.01 in = 0.254 mm resolution)."
plots:
  - title: Runoff, infiltration and overflow
    ylabel: Flow (m³/day)
    series:
      - {column: "Runoff_flow", label: "Runoff into the basin"}
      - {column: "Infiltration_flow", label: "Infiltration through the floor"}
      - {column: "Overflow_flow", label: "Overflow"}
    caption: Infiltration is limited to a few hundred m³/day, so runoff peaks are stored in the basin. Only the 118 mm storm on day 60 overfills it.
  - title: Ponding depth in the basin
    ylabel: Depth (m)
    series:
      - {column: "Basin_depth", label: "Water depth"}
    caption: Most storms pond less than 0.35 m, which drains within a day. The day 60 storm fills the basin past the 1.0 m overflow crest and keeps it ponded for about two days.
  - title: Water content through the unsaturated zone
    ylabel: Volumetric water content (-)
    series:
      - {column: "Vadose_01_theta", label: "0 to 0.3 m"}
      - {column: "Vadose_04_theta", label: "0.9 to 1.2 m"}
      - {column: "Vadose_07_theta", label: "1.8 to 2.1 m"}
      - {column: "Vadose_10_theta", label: "2.7 to 3.0 m"}
    caption: Each storm sends a wetting front down the profile; deeper layers respond later and more smoothly. In the day 60 storm the whole profile saturates.
  - title: Recharge to the water table
    ylabel: Flow (m³/day)
    series:
      - {column: "Recharge_flow", label: "Recharge"}
    caption: Recharge is a damped, delayed version of the infiltration, except in the day 60 storm, when the saturated column passes the infiltration almost immediately.
---

## What this model represents

An infiltration basin is an open, flat-floored depression that captures stormwater and lets it soak into the ground. It reduces runoff volume and peaks downstream and recharges the aquifer, provided the soil below is permeable enough and the water table is deep enough. Two questions dominate its design: how long the basin takes to drain after a storm, and what happens in the unsaturated (vadose) zone between the basin floor and the water table.

The model sends runoff from 1 ha of pavement into a 400 m² basin (4% of the drainage area) over sandy loam, with the water table 3 m below the floor. It runs for 72 days of real hourly rainfall, including the 118 mm storm of 30 September 2010.

## How it works

**Runoff and ponding.** The `Paved_Catchment` (`Catchment`) produces kinematic-wave runoff, Q = 86400·(W/n)·S₀^0.5·h^(5/3) m³/day, with h the water depth on the pavement. The `Basin` is a `Pond` block with S = α·d^β and β = 1, which makes it a prism with a constant area α = 400 m²: depth d = S/400 (OpenHydroQual evaluates d = S²/(α(S + 0.1)), which differs only for nearly empty storage). Rain falls on its full area. The `Overflow` weir spills to the swale when the depth exceeds 1.0 m.

**Infiltration.** The `Infiltration` link (`surfacewater_to_soil_link`) uses the saturated conductivity of the top layer:

  Q = (H_basin − H_1) · K_sat / (D₁/2) · min(A_basin, A_soil) · d/(d + 0.001)

where H_basin = d (the floor is at 0 m), H_1 is the head of the top soil layer and D₁ = 0.3 m. The last factor shuts the flow off smoothly as the basin empties. When the soil is dry its suction makes H_1 strongly negative, so infiltration starts fast and then slows as the top layer wets up.

**Unsaturated zone.** Each `Soil` block holds water S = θ·A·D. Effective saturation and pressure head follow van Genuchten:

  Se = (θ − θ_r)/(θ_s − θ_r), limited to 0.001 to 0.999
  ψ = −(1/α)·(Se^(−1/m) − 1)^(1/n),  m = 1 − 1/n

Above 99.9% saturation, extra water builds positive pressure through the specific storage (0.01 1/m). The head of a block is H = z_bottom + D + ψ (referenced to the top of the block). Flow between adjacent layers (`soil_to_soil_link`) is

  Q = K_eff · (H_upper − H_lower) / L · A,  K_eff = K_sat · [1 − (1 − Se^(1/m))^m]²

with L = 0.3 m and Se taken from the wetter of the two layers. This is a finite-volume form of Richards' equation with ten cells.

**Recharge.** The `Recharge` link (`soil_to_fixedhead_link`) is Q = (H_10 − H_wt)·K_eff/(D/2)·A, with H_wt = −3 m. Because H_10 is referenced to the top of the bottom layer, the gravity gradient across this link is 2 when that layer is saturated.

## What to look for in the results

- **Water budget.** The 240 mm of rain delivers 2,500 m³ (2,400 m³ of runoff and 96 m³ of direct rain on the basin). Of this, 2,067 m³ infiltrates (83%) and 390 m³ overflows (16%), all of it in the day 60 storm. By the end, 2,037 m³ has reached the water table and about 85 m³ is still held in the unsaturated zone.
- **Drawdown.** Ordinary storms (up to 30 mm) pond 0.1 to 0.35 m and drain within a day. The day 60 storm fills the basin to 1.06 m; the basin stays ponded for about 51 hours from the start of the rain, close to the 48 to 72 hour limit commonly used in design.
- **Infiltration rate.** Infiltration peaks at about 700 m³/day (1.75 m/day over the floor) at the start of the day 11 storm, faster than K_sat, because the dry soil's suction adds to the driving head. Later in each storm, and on wetter soil, it falls back toward the saturated rate.
- **Wetting fronts.** After the day 4 and day 11 storms, the water content rises first at the top and reaches 1 to 3 m depth over the following day, with lower and broader peaks. During long dry spells the profile drains toward 0.13 to 0.25.
- **Full saturation.** During the day 60 storm, all ten layers reach saturation (θ ≈ 0.41) within an hour. The column then behaves like a saturated sand filter, and recharge (up to 504 m³/day) follows the infiltration almost without delay.
- **Capillary rise.** For the first 6 days, the recharge flow is slightly negative (less than 1 m³/day): the initially dry bottom layer draws water up from the water table.

## Assumptions and limitations

- Flow is one-dimensional and vertical. Lateral spreading below the basin and groundwater mounding are not represented: the water table is fixed at −3 m, so recharge never raises it. A shallow water table that rises under the basin would slow drawdown considerably.
- The soil is uniform sandy loam with textbook van Genuchten parameters, and the basin floor does not clog. In practice, fine sediment reduces the floor conductivity over time.
- The basin has vertical sides, so infiltration takes place through the 400 m² floor only.
- Infiltration uses the saturated conductivity of the top layer, so it is a good approximation once the surface is wet but slightly overestimates infiltration into very dry soil.
- There is no evaporation from the basin or the soil and no vegetation.
- The catchment has no losses and no depression storage.
- The ten 0.3 m layers resolve wetting fronts only approximately; a sharper front needs thinner layers and a longer run time.
