---
title: Hillslope Hydrologic Response Units
track: hydro
level: 2
status: ready
doc: hydrologic_response_units.pdf
summary: A hillslope built from two hydrologic response units. Each bundles a surface, a three-layer soil column and a groundwater cell. Overland flow runs from the upper unit onto the lower one, groundwater flows downslope, and the lower unit feeds a stream by surface runoff and baseflow.
plugins: [hydrologic_response_unit, unsaturated_soil, groundwater, soil_evapotranspiration_models]
features: [HRU composites, Hillslope cascade, Run-on infiltration, Saturation excess, Groundwater throughflow]
keywords: [hru, hydrologic response unit, hillslope, toe slope, lumped, semi-distributed, watershed, infiltration, infiltration excess, saturation excess, run-on, variable source area, interflow, throughflow, recharge, baseflow, soil moisture, van genuchten, evapotranspiration, water balance]
components:
  Rain: 'Hourly rainfall for 30 days: five storms of 22 to 40 mm, 149 mm in total. Falls on the surface of both units.'
  ET: Reference evapotranspiration (about 2.6 mm/day) withdrawn from the top soil layer of both units, scaled by that layer's relative wetness θ/θ_sat (correction factor 1).
  Upslope: 'Upper hillslope unit: 2 ha, surface at 100 m, 5 m of unsaturated clay-loam soil over an 8 m groundwater cell. The water table starts at 91 m, 4 m below the soil column. Steeper (5%) and with a deep unsaturated zone.'
  Downslope: 'Toe-slope unit next to the stream: 2 ha, surface at 94 m, only 1.4 m of soil over a 6.6 m groundwater cell. The water table starts at 90.5 m. Flatter (2%), with a thin soil column that can fill during storms.'
  Stream: Fixed-head block at 88 m standing for the stream at the foot of the slope. Its storage starts at zero and accumulates both surface runoff and baseflow.
  Overland_flow: Sheet flow from the surface of `Upslope` onto the surface of `Downslope`, where it can infiltrate again (run-on).
  Runoff_to_stream: Sheet flow from the surface of `Downslope` into the stream.
  Groundwater_throughflow: 'Darcy flow from the groundwater cell of `Upslope` to that of `Downslope` across a 1200 m² saturated cross-section over 200 m. Positive downslope; it reverses if the lower water table rises above the upper one.'
  Baseflow_to_stream: 'Darcy flow from the groundwater cell of `Downslope` to the stream across a 400 m² seepage face over 100 m. Positive toward the stream.'
inputs:
  precipitation.csv: 'Hourly rainfall depth. Three columns, no header: interval start (days), interval end (days), depth in the interval (m). 720 intervals over 30 days.'
  evapotranspiration.csv: Daily reference evapotranspiration (m/day) versus time (days). Two columns, no header. 2.36 to 2.87 mm/day.
plots:
  - title: Rainfall
    ylabel: Intensity (m/day)
    series:
      - {column: "Rain_Intensity", label: "Rain"}
    caption: Five storms. The storm on day 7.5 is the largest (40 mm) and the most intense (8 mm/h).
  - title: Surface flows
    ylabel: Flow (m³/day)
    series:
      - {column: "Overland_flow_flow", label: "Upslope → Downslope (overland)"}
      - {column: "Runoff_to_stream_flow", label: "Downslope → Stream (surface runoff)"}
    caption: Surface runoff appears only in three storms and is mostly produced on the toe slope. The upper unit sheds little water, and much of it soaks in again on the way down.
  - title: Top-soil moisture
    ylabel: Moisture content θ (–)
    series:
      - {column: "Upslope__Soil_1_theta", label: "Upslope, layer 1 (0 to 0.71 m)"}
      - {column: "Downslope__Soil_1_theta", label: "Downslope, layer 1 (0 to 0.2 m)"}
      - {column: "Downslope__Soil_2_theta", label: "Downslope, layer 2 (0.2 to 0.6 m)"}
    caption: The thin top layer of the toe slope wets quickly and comes close to saturation (θ_sat = 0.41) in the storms on days 7.5 and 25.5. The thicker upslope layer stays well below saturation.
  - title: Subsurface flows
    ylabel: Flow (m³/day)
    series:
      - {column: "Upslope__recharge_flow", label: "Recharge, Upslope"}
      - {column: "Downslope__recharge_flow", label: "Recharge, Downslope"}
      - {column: "Groundwater_throughflow_flow", label: "Groundwater throughflow"}
      - {column: "Baseflow_to_stream_flow", label: "Baseflow to stream"}
    caption: Upslope, recharge is only the drainage of the initial soil water, which fades within about five days; the storms do not reach the deep bottom layer within the month. On the toe slope, recharge rises after each storm. Baseflow is steady at about 50 m³/day because the groundwater heads barely move.
---

## What this model represents

A hydrologic response unit (HRU) is a piece of land treated as one hydrological column: a surface, a soil profile and a groundwater store, with the fluxes between them. Semi-distributed watershed models (SWAT, PRMS, and many others) build a watershed from HRUs. OpenHydroQual provides the HRU as a composite block, so a whole land column is added as a single object with one set of properties.

This model is a hillslope with two units in series: a steeper **upslope** unit with a deep unsaturated zone, and a flatter **toe-slope** unit with a thin soil next to the stream. Surface water and groundwater both move downslope from one unit to the next. The model shows how such a cascade generates streamflow, and why runoff tends to come from the wet land near the stream (the variable-source-area idea).

## How it works

Each `Hydrologic_Response_Unit` contains five members and four internal links. In the output their names carry the unit name as a prefix, for example `Downslope__Soil_1_theta` or `Upslope__recharge_flow`.

| Member | What it is | Upslope | Downslope |
|---|---|---|---|
| `Catchment` | Surface store that receives rain | at 100 m | at 94 m |
| `Soil_1` | Top soil layer, D/7 thick | 0.71 m | 0.20 m |
| `Soil_2` | Middle layer, 2D/7 | 1.43 m | 0.40 m |
| `Soil_3` | Bottom layer, 4D/7 | 2.86 m | 0.80 m |
| `Groundwater` | Groundwater cell below the soil | 8 m, base at 87 m | 6.6 m, base at 86 m |

D is the depth to groundwater (5 m and 1.4 m). Both units have a plan area A = 20,000 m² and the same clay-loam soil: K_sat = 0.06 m/day, van Genuchten α = 1.9 1/m, n = 1.31, θ_sat = 0.41, θ_res = 0.095.

**Surface.** Rain falls on the `Catchment` member. Water on the surface leaves by infiltration, or as sheet flow when its depth d exceeds the depression storage d_s (1 mm):

  Q = 86400 · (W/n) · S^0.5 · max(d − d_s, 0)^(5/3)  (m³/day)

with width W = 200 m, slope S and Manning roughness n (0.05 and 0.1 upslope, 0.02 and 0.12 downslope). `Overland_flow` delivers the upslope sheet flow to the downslope surface, where it can infiltrate (run-on). `Runoff_to_stream` delivers the downslope sheet flow to the stream.

**Soil water.** Each layer has the van Genuchten relations between moisture content θ, effective saturation S_e = (θ − θ_res)/(θ_sat − θ_res) and suction head ψ:

  ψ = −(1/α)·(S_e^(−1/m) − 1)^(1/n),  k_r = [1 − (1 − S_e^(1/m))^m]²,  m = 1 − 1/n

and its total head is h = bottom elevation + layer thickness + ψ. Flow between members is Darcy flow driven by head differences:

- Infiltration (surface to `Soil_1`): Q = A·K_sat·(h_surface − h_1)/(d_1/2), switched off smoothly when no water is ponded. While the top layer is dry, its suction makes the infiltration capacity several times K_sat.
- Percolation (`Soil_1` to `Soil_2`, `Soil_2` to `Soil_3`): Q = A·K_sat·k_r·(h_i − h_j)/L, with k_r evaluated at the wetter of the two layers and L the mean thickness. It can be upward (capillary rise).
- Recharge (`Soil_3` to `Groundwater`): Q = A·K_r·(h_3 − h_g)/L with the constant recharge conductivity K_r = 0.06 m/day and L = (d_3 + b)/2, b being the groundwater cell thickness.
- Evapotranspiration from `Soil_1`: E = corr_fact · ET₀ · A · θ/θ_sat.

**Groundwater.** The groundwater cell stores water as a moisture content θ_g over its volume A·b. Its head is h_g = base + b + (θ_g − φ)/S_s with porosity φ = 0.25. The specific storage is set to S_s = φ/b (0.031 and 0.038 1/m), which makes h_g = base + θ_g·b/φ, the elevation of a free water table. The initial moisture contents (0.125 and 0.171) put the water tables at 91 m and 90.5 m.

**Between the units and to the stream.** `Groundwater_throughflow` is Q = A_x·K̄·(h_up − h_down)/L with A_x = 1200 m², K̄ = 5 m/day and L = 200 m, about 15 m³/day at the start. `Baseflow_to_stream` is Q = A_b·K·(h_down − h_stream)/L with A_b = 400 m², K = 5 m/day, L = 100 m and the stream at 88 m, about 50 m³/day.

## What to look for in the results

- **Where runoff comes from.** Of 149 mm of rain, only 7.3 mm leaves as surface runoff, in three storms. The upslope unit sheds 59 m³ of overland flow in total, and in the storm on day 20 most of it re-infiltrates on the toe slope (18 m³ arrives, 5 m³ reaches the stream).
- **Infiltration excess.** In the storm on day 7.5 (8 mm/h) the rain rate exceeds the infiltration capacity on both units. Runoff to the stream peaks at 1630 m³/day.
- **Saturation excess.** By day 25.5 the thin top layer of the toe slope is almost saturated (θ = 0.403 of 0.41). In the last storm the toe slope produces 115 m³ of runoff although the rain is less intense, while the upper unit contributes only 34 m³.
- **Slow subsurface.** On the toe slope, with only 1.4 m of soil, recharge rises within a day or two of each storm. Upslope, the 5 m soil column absorbs the storms: the wetting fronts stay in the upper two layers and the bottom layer keeps draining slowly, so recharge there is only the decay of the initial drainage toward equilibrium with the water table (the peak at the start). Over one month the water tables move by less than 0.13 m, so throughflow (15 to 20 m³/day) and baseflow (about 50 m³/day) are nearly constant.
- **Water balance.** Over the 4 ha hillslope, in mm of water:

| Term | m³ | mm |
|---|---|---|
| Rain | 5947 | 148.7 |
| Evapotranspiration | −2466 | −61.7 |
| Surface runoff to the stream | −292 | −7.3 |
| Baseflow to the stream | −1486 | −37.2 |
| Increase in soil water | 1516 | 37.9 |
| Increase in groundwater | 184 | 4.6 |

The terms close to within 1.2 m³ (0.02% of the rain).

## Assumptions and limitations

- Each unit is laterally uniform: one surface depth, one moisture content per layer and one water table for 2 ha. Gradients inside a unit are not resolved.
- The three soil layers share one set of soil properties. Evapotranspiration is taken only from the top layer and is proportional to its relative wetness.
- Recharge uses a constant conductivity. This is adequate here because the water tables lie only 2 to 4 m below the soil columns; for deep water tables the Urban HRU recharges through the unsaturated conductivity instead (see the technical guide).
- The stream is a fixed head at 88 m, so stream stage does not respond to the inflow.
- Surface runoff is sheet flow with no channel; the depression storage holds water that only infiltrates (there is no surface evaporation).
- The groundwater cell is the confined-type `Groundwater cell`. Setting S_s = φ/b gives it a water-table response, but its storage is not limited at the top of the cell.
