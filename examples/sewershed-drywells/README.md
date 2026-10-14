---
title: Sewershed with Infiltration Pond and Drywell
track: storm
level: 3
status: ready
summary: An 11.3 ha urban sewershed in an arid climate drains through two storm-sewer lines into an infiltration pond with a 42 m drywell. A 133-cell radial grid follows the injected water through 70 m of layered vadose zone, and a build-up and wash-off pollutant tracks the first flush.
plugins: [Sewer_system, Well, unsaturated_soil, Pond_Plugin, buildup_washoff, soil_evapotranspiration_models]
features: [Large model (163 blocks, 302 links), Drywell injection, Radial vadose-zone grid, Build-up and wash-off, Observed weather forcing]
keywords: [drywell, dry well, class v injection well, infiltration basin, infiltration pond, sewershed, storm sewer, pipe network, managed aquifer recharge, stormwater capture, groundwater recharge, vadose zone, unsaturated flow, van genuchten, radial grid, axisymmetric, build-up, wash-off, first flush, pollutant transport, penman, arid climate, case study, large model]
components:
  Rain: "Hourly precipitation for 18 November to 10 December 2018 (103 mm in three storms). It falls on the 13 catchments."
  Soil_ET: "Penman evapotranspiration from the top soil layer under the pond, driven by hourly air temperature, relative humidity, solar radiation and wind speed at the same location."
  Buildup: "Constant build-up of the surface pollutant on every catchment, 0.01 g/m²/day."
  Pollutant_surface: "Pollutant bound to the catchment surfaces (g/m²). Starts at 1 g/m², the load accumulated over about 100 dry days, and grows by Buildup between storms."
  Pollutant: "Dissolved pollutant (g/m³) carried by the water from the catchments through the sewers, the pond, the drywell and the soil."
  k_washoff: "Wash-off rate coefficient, 10⁶ (1/m²/day when multiplied by the squared water depth)."
  Washoff: "Transfer from Pollutant_surface to Pollutant on wet surfaces, at a rate of k_washoff × load × depth² per unit area."
  Catchment: "13 paved sub-catchments, Catch_01 to Catch_13 (2,600 to 33,300 m², 11.3 ha in total), each draining along one sewer segment (overland flow width equal to the segment length, slope 0.015, Manning n = 0.2, no depression storage, no infiltration)."
  Sewerchannelsegment: "13 segments of 0.914 m (36 inch) storm sewer, 9 to 116 m long, Manning n = 0.1, in two lines: Sewer_05 to Sewer_01 (inverts 7.5 to 2.2 m) and Sewer_13 to Sewer_06 (inverts 10.7 to 2.4 m)."
  Pond: "Infiltration pond receiving both sewer lines. Stage-storage S = 86.06·d^2.766: 519 m³ and about 750 m² of water surface at the 1.914 m spillway crest. It drains into the drywell, into the soil beneath it and over its spillway."
  Overflow: "Fixed-head boundary (0 m) that receives the spillway overflow and carries it off site. The spillway flow depends only on the pond level, so this head does not affect the result."
  Drywell: "Drywell 2 m in diameter and 41.95 m deep (bottom at −41.95 m), starting empty. Water leaves through its wall into the ten soil layers it penetrates and through its bottom."
  Water_Table: "Fixed-head boundary at −70.28 m: the regional water table at the base of the soil grid."
  Soil: "133 van Genuchten soil cells in an axisymmetric grid around the drywell: 13 layers (L01 to L13) by 10 rings (R01 to R10, outer radii 1.96 to 26.0 m) plus a column under the well (R00, layers 11 to 13 only). Cell Lii_Rjj is layer ii of ring jj. Layer properties are listed in the table under How it works."
  Catchment_link: "Kinematic sheet flow from each catchment into its sewer segment."
  Sewer2Sewer_link: "Manning flow between consecutive sewer segments, driven by the head difference."
  Outfall_01: "sewer2pond link: outfall of the Sewer_05 to Sewer_01 line into the pond."
  Outfall_06: "sewer2pond link: outfall of the Sewer_13 to Sewer_06 line into the pond."
  Overflow_weir: "Spillway of the pond: Q = 392,619·(h − 1.914)^2.995 m³/day."
  Drywell_inlet: "Inflow from the pond into the drywell around its 2 m rim. Negative when the well head exceeds the pond level."
  surfacewater_to_soil_link: "Infiltration from the pond into the top cell of each ring (Infiltration_R01 to R10)."
  Well2soil horizontal link: "Radial flow from the drywell through its wall into the ring-1 cell of each of layers 1 to 10 (Injection_L01 to L10). Negative when the soil drains back into the well."
  Injection_bottom: "Flow through the bottom of the drywell into the cell beneath it (L11_R00)."
  soil_to_soil_link: "Vertical unsaturated flow between stacked cells (Vertical_Lii_Rjj)."
  soil_to_soil_H_link: "Radial unsaturated flow between neighbouring rings (Radial_Lii_Rjj), over a cylindrical interface of area 2π·r·thickness."
  soil_to_fixedhead_link: "Drainage from the bottom layer (L13) of each column into the water table (Recharge_R00 to R10)."
inputs:
  precipitation.csv: "Hourly precipitation. Three columns, no header: interval start (day), interval end (day), depth in the interval (m). Day 0 is 18 November 2018 00:00 local standard time."
  air_temperature.csv: "Hourly air temperature at 2 m (°C), two columns: time (day), value. Same period and time base as the precipitation."
  relative_humidity.csv: "Hourly relative humidity at 2 m as a fraction (0 to 1), two columns: time (day), value. Same period and time base as the precipitation."
  solar_radiation.csv: "Hourly incoming shortwave radiation at the surface (W/m²), two columns: time (day), value. Same period and time base as the precipitation."
  wind_speed.csv: "Hourly wind speed (m/s), two columns: time (day), value. Same period and time base as the precipitation."
plots:
  - title: Rainfall
    ylabel: Intensity (m/day)
    series:
      - {column: "Rain_Intensity", label: "Rain intensity"}
    caption: "Three storms: 9 mm on 21 and 22 November (days 3 and 4), 30 mm on 29 November (day 11) and 61 mm on 5 to 7 December (days 17 to 19)."
  - title: Pond inflow and outflows
    ylabel: Flow (m³/day)
    series:
      - {column: "Outfall_01_flow", label: "Sewer line 1 (outfall 01)"}
      - {column: "Outfall_06_flow", label: "Sewer line 2 (outfall 06)"}
      - {column: "Overflow_weir_flow", label: "Spillway overflow"}
      - {column: "Drywell_inlet_flow", label: "Into the drywell"}
    caption: "The first storm is fully captured and the second almost fully (150 m³ spills). In the third storm the pond is already full and most of the inflow leaves over the spillway; the drywell, also full, takes almost nothing."
  - title: Pond water depth
    ylabel: Depth (m)
    series:
      - {column: "Pond_depth", label: "Infiltration pond"}
    caption: "The pond drains within a few days after the small first storm. After the second storm it stays near its 1.914 m crest, because the soil below it is saturated down to a low-permeability layer."
  - title: Drywell water depth
    ylabel: Depth (m)
    series:
      - {column: "Drywell_depth", label: "Drywell"}
    caption: "The 42 m drywell fills in the first storm and drains to 14 m over the following week. From the second storm on it stays full, with its water level tied to the pond."
  - title: Soil moisture next to the drywell
    ylabel: Moisture content (–)
    series:
      - {column: "L01_R01_theta", label: "Layer 1 (0 to 4.2 m), ring 1"}
      - {column: "L05_R01_theta", label: "Layer 5 (20.6 to 26.7 m), ring 1"}
      - {column: "L09_R01_theta", label: "Layer 9 (35.9 to 38.9 m), ring 1"}
      - {column: "L09_R05_theta", label: "Layer 9, ring 5 (r = 6 to 8 m)"}
      - {column: "L11_R00_theta", label: "Layer 11, under the well"}
    caption: "Cells beside the drywell saturate within hours of the first injection. The wetting front in the permeable layer 9 spreads outward and reaches ring 5 days later."
  - title: Surface pollutant load
    ylabel: Load (g/m²)
    series:
      - {column: "Catch_04_Pollutant_surface:concentration", label: "Catch_04"}
    caption: "The first storm washes off nearly all of the accumulated 1 g/m². Between storms the load rebuilds at 0.01 g/m²/day, so the later, larger storms carry much less pollutant."
  - title: Pollutant load into and out of the pond
    ylabel: Load (g/day)
    series:
      - {column: "Outfall_01_Pollutant:masstransfer", label: "Sewer line 1 (outfall 01)"}
      - {column: "Outfall_06_Pollutant:masstransfer", label: "Sewer line 2 (outfall 06)"}
      - {column: "Overflow_weir_Pollutant:masstransfer", label: "Over the spillway"}
    caption: "The first flush (day 4) delivers up to 150 kg/day per sewer line and none of it spills. The spillway carries 10.5 kg off site, 9.8 kg of it in the third storm."
  - title: Pollutant stored in the drywell and the pond
    ylabel: Mass (g)
    series:
      - {column: "Drywell_Pollutant:mass", label: "In the drywell"}
      - {column: "Pond_Pollutant:mass", label: "In the pond"}
    caption: "The first flush fills the drywell with 12.8 kg of pollutant, which then moves into the surrounding soil (121 kg are in the soil by the end, not plotted)."
---

## What this model represents

In arid and semi-arid cities, stormwater is increasingly treated as a resource: it is collected by the storm-sewer network and infiltrated, in place of being sent to the ocean. Where the near-surface soils are tight, **drywells** are used: vertical shafts, here 2 m wide and 42 m deep, that bypass the surface layers and put the water directly into deeper, more permeable strata. Their performance depends on how much water the surrounding vadose zone can accept, and their risk depends on what the water carries: the first flush of a storm washes the pollutants accumulated on streets and roofs during the dry season straight into the drywell.

This model is a complete small sewershed with such a system:

- **13 paved sub-catchments** (11.3 ha) drain into **two 0.91 m storm-sewer lines**.
- Both lines discharge into an **infiltration pond** (519 m³ at its spillway crest).
- The pond drains into a **42 m drywell**, infiltrates through its floor, and spills to a downstream outlet when full.
- An **axisymmetric grid of 133 soil cells** (13 layers by 11 columns) represents the 70 m vadose zone around the drywell down to the water table.
- A **build-up and wash-off** pollutant is carried from the catchment surfaces through the sewers, the pond and the drywell into the soil.

It is driven by hourly precipitation and weather for the first storms of the 2018 to 2019 wet season, 18 November to 10 December 2018. It is the largest example in this collection (163 blocks and 302 links) and runs in about five minutes.

## How it works

**Catchments and sewers.** Each catchment is a paved surface without infiltration or depression storage. Rain enters its storage and drains by kinematic sheet flow to its sewer segment,

  Q = 86400 · (W/n) · S^½ · d^(5/3)

with the width W equal to the length of the segment it drains along, S = 0.015 and n = 0.2. Sewer segments are `Sewerchannelsegment` blocks: the depth follows from the stored volume through a polynomial fit of a circular section, and the head is invert + depth. Consecutive segments are joined by Manning links,

  Q = 86400 · (1/n̄) · A · R^(2/3) · √(Δh/L̄)

where A is the flowing area of the segment with the higher head, R the hydraulic radius from the mean wetted perimeter, n̄ and L̄ the mean roughness and mean length. The last segment of each line discharges into the pond through a `sewer2pond` link, the same Manning relation with the upstream flowing area (free outfall: the sewer inverts are above the pond crest). The two lines meet only in the pond.

**Infiltration pond (`Pond`).** Storage and depth are related by S = 86.06·d^2.766, so the water surface area is 238·d^1.766 m² (about 750 m² at the crest). Water leaves the pond in three ways:

- over the **spillway**, Q = 392,619 · (h − 1.914)₊^2.995 m³/day;
- into the **drywell** around its rim, Q = 86400 · √((h_pond − h_well)/L) / n · π·D · d_pond^(5/3) with L = 3 m, n = 100 and D = 2 m (negative when the well level is higher);
- through its **floor** into the top cell of each ring, Q = K_sat · (h_pond − h_soil)/(Δz/2) · min(A_pond, A_cell), switched off smoothly as the pond empties.

**Drywell.** The well is a cylinder with storage π·D²/4 · depth. Each wall link is

  Q = K_sat · [ (h_well − h_soil)₊ · A_wet / L − (h_soil − z_top)₊ · A_cell / L ] · d_well/(d_well + 0.01)

with L = 0.48 m (from the well wall to the centre of ring 1), A_wet = π·D times the wetted height of that layer, A_cell = π·D times the full layer thickness, and z_top the top of the layer. The first term is injection from the well; the second lets a layer whose pressure head is positive drain back into the well. The bottom link is Darcy flow through the 3.14 m² base into the cell below.

**Vadose zone.** Every soil cell is a van Genuchten block: moisture content θ = V/(A·Δz), effective saturation S_e, suction ψ = −(1/α)·(S_e^(−1/m) − 1)^(1/n) with m = 1 − 1/n, and head h = z_bottom + Δz + ψ. Above saturation the cell stores water elastically with specific storage S_s = 0.001 1/m. Vertical links use

  Q = A · K_sat · k_r(S_e) · (h_upper − h_lower) / L,  k_r = [1 − (1 − S_e^(1/m))^m]²

with the larger S_e of the two cells, the smaller K_sat and L the distance between cell centres. Radial links use the same relation with the mean K_sat and the cylindrical interface 2π·r·Δz between rings. The rings have outer radii 1.96, 3.12, 4.51, 6.17, 8.17, 10.6, 13.4, 16.9, 21.0 and 26.0 m; the outer boundary at 26 m is closed. The bottom layer drains to the water table at −70.28 m. The layers (K_sat already multiplied by the calibrated factor of 40 applied to every cell):

| Layers | Depth (m) | K_sat (m/day) | α (1/m) | n | θ_s |
|---|---|---|---|---|---|
| 1 and 2 | 0 to 8.4 | 2.8 | 2.49 | 1.17 | 0.392 |
| 3 to 5 | 8.4 to 26.7 | 0.011 | 4.3 | 1.52 | 0.366 |
| 6 to 8 | 26.7 to 35.9 | 0.0035 | 0.159 | 1.21 | 0.285 |
| 9 | 35.9 to 38.9 | 0.53 | 0.405 | 1.19 | 0.348 |
| 10 to 13 | 38.9 to 70.3 | 0.011 | 4.3 | 1.52 | 0.366 |

All cells start at θ = 0.2. The top layer loses water by Penman evapotranspiration, E = [Δ·E_r + γ·E_a]/(Δ + γ), with E_r the incoming solar radiation converted to an evaporation rate, E_a = B·e_s(T)·(RH − 1) the aerodynamic term and B a function of wind speed and roughness height (0.3 mm), scaled by θ/θ_s.

**Pollutant.** `Pollutant_surface` is an immobile load (g/m²) on the catchments. It grows by `Buildup` at 0.01 g/m²/day and is converted into the dissolved `Pollutant` by `Washoff` at a rate, per unit area,

  r = k_washoff · L_s · d²

with L_s the surface load and d the water depth on the surface. With k_washoff = 10⁶, the rate constant k_washoff·d² is 1 per day at 1 mm of water and 100 per day at 1 cm, so a storm that produces a few millimetres of sheet flow strips the surface within hours. The dissolved pollutant moves with the water by advection through every link (no decay, no sorption). Its build-up rate and initial load are illustrative.

**Time step.** `initial_time_step` is one hour, matching the forcing data, and `max_timestep_increase_factor = 1` keeps the steps at one hour or less.

## What to look for in the results

- **Fast surface, slow subsurface.** The sewers deliver 11,680 m³ to the pond, 103 mm on the paved area, with hourly peaks near 4,900 m³/day per line. The vadose zone accepts water at a few hundred cubic metres per day at most.
- **The drywell saturates its surroundings.** In the first storm (day 4) the empty drywell takes 940 m³/day and fills to 39 m within a day. The ring-1 cells beside it saturate in hours. Almost all of the drywell's outflow goes into layer 9, the only permeable stratum it reaches (510 m³ over the run, against 10 to 60 m³ for each of the tight layers). The well then drains slowly and is still 14 m deep a week later.
- **Back-flow into the well.** Layers 1 and 2 are wetted from above by infiltration through the pond floor. Once their pressure head is positive they drain back into the drywell (about 570 m³ over the run, shown by the negative injection in those layers). The drywell is then partly a conduit that carries water from the shallow soil down to layer 9.
- **The pond becomes perched.** Pond infiltration saturates layers 1 and 2, but layer 3 (K_sat = 0.011 m/day) lets water through at only about 20 m³/day across the 2,120 m² grid. From the 30 mm storm on day 11, the pond stays near its crest and the drywell stays full, so the 61 mm storm of days 17 to 19 mostly overflows: 6,420 m³ (55 % of the inflow over the whole run, almost all of it in that storm) leaves over the spillway. Floor infiltration takes 4,490 m³ (38 %) and the drywell only 300 m³ (3 %).
- **First flush.** The first storm washes almost all of the initial 113 kg of surface pollutant off the catchments; the sewer outfalls carry up to 150 kg/day and the pond concentration exceeds 100 g/m³. This load arrives while the pond and drywell still have room: by day 5, 83 kg have entered the soil under the pond and around the drywell and 12.7 kg are in the drywell. Only 10.5 kg (8 % of the 138 kg supplied, including build-up) leaves over the spillway, mostly in the third storm, which washes off the 5 to 6 kg rebuilt since the first storm together with pollutant left in the pond. The pollutant mass balance closes to 0.03 %: at the end 121 kg are in the soil, 1.9 kg in the drywell, 1.2 kg in the pond and 3.1 kg still on or over the catchments, and 10.5 kg have left over the spillway.
- **Nothing reaches the water table yet.** Only 3.7 m³ of water and practically no pollutant reach −70 m in 22 days; this drainage comes from the initial moisture of the deep layers. Travel times through the tight layers are years.

## Assumptions and limitations

- **Shortened period.** The author's original model ran three years (2018 to 2020); this version covers the first three storms of the 2018 to 2019 season so that it runs in minutes. Long-term questions (seasonal drainage of the drywell, arrival at the water table) need the longer run.
- **Calibrated values.** Manning n = 0.2 for the catchments and 0.1 for the sewers, and the factor of 40 on all soil conductivities, are calibrated values carried over from the original model. A Manning n of 0.1 is much rougher than a concrete pipe (about 0.013); it compensates for storage and delays the model does not represent explicitly (inlets, laterals, manholes).
- **Pond infiltration area.** Each pond-to-soil link uses the smaller of the pond surface and the ring area. Summed over the ten rings this exceeds the actual pond surface (at the crest, 2,120 m² against about 750 m²), so floor infiltration is overestimated while the pond is shallow.
- **Closed outer boundary.** No water leaves the grid sideways beyond 26 m. Lateral spreading in layer 9 is therefore limited, which keeps the drywell full longer than in an unbounded formation.
- **Uniform initial moisture.** All cells start at θ = 0.2, which is not in equilibrium with the layering; the deep layers drain slowly during the run.
- **Paved catchments.** All catchment area is impervious and connected; there is no pervious area or interception.
- **Generic pollutant.** The pollutant is conservative and dissolved; no sorption to soil, decay or particle settling in the pond.
- **Evapotranspiration** uses incoming shortwave radiation without albedo or long-wave losses, which overestimates the radiation term.
