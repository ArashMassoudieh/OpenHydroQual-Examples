---
title: Urban HRU to Stream
track: hydro
level: 2
status: ready
doc: hydrologic_response_units.pdf
summary: A 50 ha urban neighborhood, 25% directly connected impervious, modeled as one Urban HRU that drains to an 800 m stream. Impervious runoff reaches the stream within hours, while rain on lawns infiltrates, recharges an unconfined aquifer and returns slowly as baseflow.
plugins: [urban_hru, unsaturated_soil, unconfined_groundwater, open_channel, soil_evapotranspiration_models]
features: [Impervious and pervious surfaces, Layered van Genuchten soil, Unsaturated-conductivity recharge, Unconfined aquifer, GW-stream exchange]
keywords: [urban hru, hydrologic response unit, impervious, imperviousness, directly connected impervious area, dcia, urbanization, urban hydrology, stormwater, infiltration, recharge, unconfined aquifer, water table, baseflow, stream, groundwater surface water, gw-sw interaction, manning, channel routing, water balance]
components:
  Rain: 'Hourly rainfall for 30 days: five storms of 22 to 40 mm, 149 mm in total. Falls on both the pervious and impervious surfaces.'
  ET: Reference evapotranspiration (about 2.6 mm/day) with a correction factor of 0.8, withdrawn from the top soil layer under the pervious surface and scaled by its relative wetness.
  Neighborhood: 'The urban HRU: 50 ha with surface at 100 m. 25% (12.5 ha) is directly connected impervious surface; the other 37.5 ha is pervious, over 3.5 m of layered soil. Below lies an unconfined aquifer (specific yield 0.15) under the whole 50 ha, with the water table at 88.5 m. Each surface drains through its own 400 m internal reach.'
  Stream: 'Receiving stream: an 800 m trapezoidal channel, 3 m base width, 2:1 side slopes, Manning n = 0.035, bed at 88 m, initial depth 0.05 m.'
  Outlet: Fixed-head boundary at 87 m at the downstream end of the stream. Its storage starts at zero and accumulates the outflow.
  Pervious_outlet: Port of the HRU's pervious-surface reach (`Reach_link`) into the stream. Manning flow driven by the head difference between the reach and the stream.
  Impervious_outlet: Port of the HRU's impervious-surface reach (`Impervious_Reach_link`) into the stream. Same equation.
  Baseflow: 'Darcy exchange between the aquifer and the stream, through an 8000 m² seepage face over 150 m with K = 5 m/day. Positive toward the stream; it reverses if the stream stage rises above the water table.'
  Stream_outlet: Manning flow from the stream to the outlet boundary (`channel2fixed`).
inputs:
  precipitation.csv: 'Hourly rainfall depth. Three columns, no header: interval start (days), interval end (days), depth in the interval (m). 720 intervals over 30 days, 149 mm in total.'
  evapotranspiration.csv: Daily reference evapotranspiration (m/day) versus time (days). Two columns, no header. 2.36 to 2.87 mm/day.
plots:
  - title: Flows into and out of the stream
    ylabel: Flow (m³/day)
    series:
      - {column: "Impervious_outlet_flow", label: "Impervious surface"}
      - {column: "Pervious_outlet_flow", label: "Pervious surface"}
      - {column: "Baseflow_flow", label: "Baseflow"}
      - {column: "Stream_outlet_flow", label: "Stream outflow"}
    caption: Storm flow in the stream is almost entirely impervious runoff. The pervious surface produces none. Between storms the stream carries only baseflow.
  - title: Recharge and baseflow
    ylabel: Flow (m³/day)
    series:
      - {column: "Neighborhood__recharge_flow", label: "Recharge to the aquifer"}
      - {column: "Baseflow_flow", label: "Baseflow to the stream"}
    caption: Recharge starts high as the initially wet bottom soil layer drains, then settles near the rate water moves through the soil column. Baseflow doubles over the month as the water table rises.
  - title: Water table
    ylabel: Elevation (m)
    series:
      - {column: "Neighborhood__Groundwater_piezometric_head", label: "Water table"}
      - {column: "Stream_head", label: "Stream water surface"}
    caption: The water table rises 0.37 m in 30 days and stays above the stream, so the stream gains water from the aquifer throughout.
  - title: Soil moisture under the pervious surface
    ylabel: Moisture content θ (–)
    series:
      - {column: "Neighborhood__Soil_1_theta", label: "Layer 1 (0 to 0.5 m)"}
      - {column: "Neighborhood__Soil_2_theta", label: "Layer 2 (0.5 to 1.5 m)"}
      - {column: "Neighborhood__Soil_3_theta", label: "Layer 3 (1.5 to 3.5 m)"}
    caption: The top layer responds to every storm and dries between them. The middle layer stores the infiltrated water. The bottom layer slowly drains toward the aquifer.
---

## What this model represents

Urbanization changes how a watershed responds to rain. Roofs, roads and parking lots connected to storm drains send rain to the stream within minutes to hours, while lawns and parks still absorb most of what falls on them. The stream gets higher, faster storm peaks, and its dry-weather flow depends on how much water still reaches the aquifer through the remaining pervious ground.

This model represents a 50 ha neighborhood as a single **Urban HRU** that drains to a short stream reach. A quarter of the area is directly connected impervious surface. It shows the split between fast impervious runoff and slow groundwater return flow, and closes the water balance over one wet month. It is the worked example of the technical guide.

## How it works

The `Urban_HRU` composite contains eight members. In the output their names carry the HRU name as a prefix, for example `Neighborhood__Soil_1_theta`.

| Member | Type | Plan area | Role |
|---|---|---|---|
| `Impervious_Catchment` | Catchment | A·f_i = 12.5 ha | Impervious surface, no soil below |
| `Catchment` | Catchment | A·(1 − f_i) = 37.5 ha | Pervious surface |
| `Impervious_Reach`, `Reach` | Trapezoidal channel, 400 m | | Collect the runoff of each surface |
| `Soil_1`, `Soil_2`, `Soil_3` | Soil, 0.5 m, 1.0 m, 2.0 m | 37.5 ha | Unsaturated profile under the pervious surface |
| `Groundwater` | Unconfined groundwater cell | A = 50 ha | Aquifer under the whole unit |

The impervious fraction is f_i = min(impervious_fraction × impervious_multiplier, 0.95) = 0.25. It must be the **directly connected** impervious area: impervious surfaces that drain onto lawns belong to the pervious surface.

**Surfaces and reaches.** Rain falls on both surfaces. Each surface drains to its own reach by sheet flow,

  Q = 86400 · (W/n) · S^0.5 · max(d − d_s, 0)^(5/3)  (m³/day)

with a shared width W = 2500 m and slope S = 0.03, and separate roughness and depression storage (n = 0.015 and d_s = 1.5 mm for the impervious surface; n = 0.15 and d_s = 5 mm for the pervious surface). The reaches and the stream use Manning's equation driven by the head difference between neighboring segments,

  Q = 86400 · (1/n̄) · A_u · R^(2/3) · ((h_r − h_c)/L̄)^0.5

where A_u is the flow area at the end with the higher head, R the hydraulic radius, n̄ and L̄ the mean roughness and length of the two segments.

**Soil.** The three layers take their own van Genuchten parameters (K_sat = 0.6, 0.4 and 0.8 m/day; α = 1.5, 1.2 and 2.0 1/m; n = 1.35, 1.35 and 1.45). Infiltration into `Soil_1` is Darcy flow across half the top layer, driven by the difference between the ponded head and the soil head, so while the soil is unsaturated the infiltration capacity is several times K_sat. Percolation between layers uses the Mualem relative conductivity k_r of the wetter layer. Evapotranspiration is E = 0.8 · ET₀ · A_1 · θ_1/θ_sat,1.

**Recharge.** The water table lies 8 m below the soil column. With a constant conductivity, recharge across such a gap would hardly depend on soil moisture. The Urban HRU therefore uses the unsaturated conductivity of the bottom layer:

  Q_r = A(1 − f_i) · K_sat,3 · [k_r(S_e,3)·(h_3 − h_g)⁺ − (h_g − h_3)⁺] / L,  L = (d_3 + b)/2

where b = 12 m is the groundwater thickness parameter and (x)⁺ = max(x, 0). Recharge therefore falls as the bottom layer drains.

**Aquifer.** The unconfined cell has head h_g = z_base + V_g/(S_y·A), with specific yield S_y = 0.15 and the base at 84.5 m. Each millimetre of recharge over the pervious area raises the water table by (1 − f_i)/S_y = 5 mm. The initial storage is computed from the initial water-table elevation of 88.5 m.

**Baseflow.** `Baseflow` is Q_b = K·A_b·(h_g − h_c)/L_b with K = 5 m/day, A_b = 8000 m², L_b = 150 m and h_c the stream water surface. It runs in either direction.

## What to look for in the results

- **Fast impervious runoff.** Of the 18,584 m³ of rain on the impervious surface, 18,370 m³ (98.8%) reaches the stream, most of it within hours of each storm. The rest is held in depression storage. The stream outflow peaks at 23,500 m³/day (0.27 m³/s) in the storm on day 7.5.
- **No pervious runoff.** The rain intensity (at most 8 mm/h) never exceeds the infiltration capacity of the lawns, so the pervious surface produces only the few cubic metres that drain from its reach at the start.
- **Recharge.** Recharge starts at about 3000 m³/day (8 mm/day over the pervious area) as the initially wet bottom layer drains, then falls with its unsaturated conductivity to about 800 m³/day. In total 33,500 m³ (89 mm over the pervious area) reaches the aquifer.
- **Baseflow.** The water table rises 0.37 m. Baseflow grows from 120 to 228 m³/day, and between storms it is the whole flow of the stream.
- **Water balance (30 days, 50 ha):**

| Term | m³ | mm over 50 ha |
|---|---|---|
| Rain | 74,336 | 148.7 |
| Evapotranspiration | −16,743 | −33.5 |
| Outflow at the outlet | −24,206 | −48.4 |
| Increase in soil water | 5,435 | 10.9 |
| Increase in groundwater | 27,854 | 55.7 |
| Increase in surface, reach and stream storage | 92 | 0.2 |

The residual is 6 m³ (0.01% of the rain).

## Assumptions and limitations

- One unit represents the whole neighborhood: one water table, one moisture content per soil layer and one ponded depth per surface.
- Only the connected impervious area is impervious. Disconnected roofs and driveways are lumped with the lawns, where rain on them can infiltrate.
- There is no evaporation from the surfaces, so water left in depression storage stays there. Evapotranspiration comes from the top soil layer only.
- The aquifer is a single cell. The stream is short and ends at a fixed head, so there is no upstream inflow and no backwater from downstream.
- The soil and aquifer parameters are illustrative, not calibrated to a site.
