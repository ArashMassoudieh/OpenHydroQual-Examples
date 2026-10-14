---
title: Riparian and Mixed-Landuse HRUs
track: hydro
level: 2
status: ready
doc: hydrologic_response_units.pdf
summary: A 100 ha watershed in which an 80 ha mixed-landuse upland drains to a headwater reach, and the stream then flows through a 20 ha riparian corridor. The riparian unit's near-stream aquifer stores stream water during storms (bank storage) and feeds it back afterwards.
plugins: [mixed_hydrologic_response_unit, riparian_urban_hru, urban_hru, unsaturated_soil, groundwater, unconfined_groundwater, open_channel, soil_evapotranspiration_models]
features: [Mixed landuse HRU, Riparian HRU, Near-stream aquifer, Bank storage, Two-way GW-stream exchange]
keywords: [riparian, riparian zone, riparian buffer, stream corridor, floodplain, near-stream aquifer, bank storage, hyporheic, gaining stream, losing stream, mixed landuse, land use, impervious, hru, hydrologic response unit, watershed, baseflow, recession, groundwater surface water, gw-sw interaction]
components:
  Rain: 'Hourly rainfall for 30 days: five storms of 22 to 40 mm, 149 mm in total. Falls on all four surfaces of the two units.'
  ET: Reference evapotranspiration (about 2.6 mm/day) with a correction factor of 0.8, withdrawn from the top soil layer of each unit and scaled by its relative wetness.
  Upland: 'Mixed-landuse upland unit (`Mixed_Hydrologic_Response_Unit`): 80 ha with surface at 110 m, 15% directly connected impervious (roads, roofs) and 85% pervious land over 3.5 m of loam. Its groundwater cell starts with the water table at 103 m. Its two surfaces drain through 600 m internal reaches to `Upper_stream`.'
  Riparian: 'Riparian corridor unit (`Riparian_Urban_HRU`): 20 ha along the lower stream with surface at 100 m, 10% impervious, and only 1.7 m of soil above a shallow water table at 98.3 m. Its groundwater is split into a regional cell (15 ha, specific yield 0.2) and a near-stream aquifer (5 ha, specific yield 0.25) that exchanges water with `Lower_stream`.'
  Upper_stream: 'Headwater reach: 1000 m trapezoidal channel, 2 m base, 2:1 side slopes, n = 0.035, bed at 101.5 m. Receives runoff and baseflow from the upland.'
  Lower_stream: 'Reach through the riparian corridor: 1000 m, 3 m base, 2:1 side slopes, n = 0.035, bed at 98.0 m. Receives the headwater flow, the riparian runoff and the near-stream exchange.'
  Outlet: Fixed-head boundary at 97 m at the watershed outlet. Its storage starts at zero and accumulates the outflow.
  Upland_pervious_runoff: Outlet of the upland pervious-surface reach to `Upper_stream` (`Reach_link`, Manning flow driven by the head difference).
  Upland_impervious_runoff: Outlet of the upland impervious-surface reach to `Upper_stream` (`Impervious_Reach_link`).
  Upland_baseflow: 'Darcy flow from the upland groundwater cell to `Upper_stream` (`groundwater_to_stream`): 4000 m² seepage face, 200 m path, K = 2 m/day. Positive toward the stream.'
  Stream_reach: Manning flow from `Upper_stream` to `Lower_stream`. This is the whole upland contribution entering the riparian corridor.
  Riparian_pervious_runoff: Outlet of the riparian pervious-surface reach to `Lower_stream`.
  Riparian_impervious_runoff: Outlet of the riparian impervious-surface reach to `Lower_stream`.
  Bank_exchange: 'Darcy exchange between the near-stream aquifer and `Lower_stream` (`unconfined_groundwater_to_stream`): 4000 m² of bank (2 banks × 1000 m × 2 m), a 12.5 m path (half the width of the riparian strip on each side), K = 5 m/day. Positive toward the stream; negative when the stream loses water to its banks.'
  Stream_outlet: Manning flow from `Lower_stream` to the outlet boundary (`channel2fixed`).
inputs:
  precipitation.csv: 'Hourly rainfall depth. Three columns, no header: interval start (days), interval end (days), depth in the interval (m). 720 intervals over 30 days, 149 mm in total.'
  evapotranspiration.csv: Daily reference evapotranspiration (m/day) versus time (days). Two columns, no header. 2.36 to 2.87 mm/day.
plots:
  - title: Streamflow
    ylabel: Flow (m³/day)
    series:
      - {column: "Stream_reach_flow", label: "Upland flow entering the corridor"}
      - {column: "Riparian_impervious_runoff_flow", label: "Riparian impervious runoff"}
      - {column: "Stream_outlet_flow", label: "Watershed outlet"}
    caption: Storm peaks come from impervious runoff, most of it from the upland. Between storms the outlet carries 4 to 6 times more water than enters the corridor from upstream.
  - title: Groundwater flows into the streams
    ylabel: Flow (m³/day)
    series:
      - {column: "Bank_exchange_flow", label: "Near-stream aquifer → lower stream"}
      - {column: "Riparian__hillslope_to_near_stream_flow", label: "Regional → near-stream aquifer (riparian)"}
      - {column: "Upland_baseflow_flow", label: "Upland groundwater → upper stream"}
    caption: The bank exchange drops sharply in every storm as the stream rises and turns negative on day 7.7, when the stream feeds its banks. The regional cell's drainage into the near-stream aquifer grows steadily as recharge builds its water table.
  - title: Riparian water levels
    ylabel: Elevation (m)
    series:
      - {column: "Riparian__Groundwater_piezometric_head", label: "Regional water table"}
      - {column: "Riparian__Near_Stream_Aquifer_piezometric_head", label: "Near-stream water table"}
      - {column: "Lower_stream_head", label: "Lower stream water surface"}
    caption: The regional water table rises with recharge, while the near-stream aquifer is held close to the stream level by its fast exchange with the stream. In the largest storm the stream briefly rises above the near-stream water table.
  - title: Recharge
    ylabel: Flow (m³/day)
    series:
      - {column: "Upland__recharge_flow", label: "Upland"}
      - {column: "Riparian__recharge_flow", label: "Riparian, to regional cell"}
      - {column: "Riparian__recharge_near_stream_flow", label: "Riparian, to near-stream aquifer"}
    caption: The upland recharge starts with a drainage of the initial soil water and then responds slowly. Under the riparian corridor the soil sits on the water table, so recharge follows each storm within about a day.
---

## What this model represents

Land use and the stream corridor both shape a watershed's response. Upland land with roads and roofs sends quick storm runoff to the headwaters. Along the stream, the riparian zone has shallow groundwater that is in direct contact with the channel. During a storm the rising stream pushes water into its banks (bank storage); afterwards that water, together with groundwater arriving from the hillslope, drains back over days to weeks. This intermediate store is what makes observed baseflow fall quickly for a week or two after each event before settling into a slow seasonal decline.

This model is a 100 ha watershed with two units:

- an 80 ha **upland** with mixed land use (`Mixed_Hydrologic_Response_Unit`, 15% impervious), draining to a headwater reach;
- a 20 ha **riparian corridor** (`Riparian_Urban_HRU`, 10% impervious) along the lower reach, with a near-stream aquifer.

The upland drains *through* the riparian corridor in the sense that all its water reaches the outlet along the lower reach, where it interacts with the riparian groundwater. The composites do not accept surface or groundwater inflow from another unit (their only inflow ports are snowmelt links and, for the riparian unit, lateral flow between unconfined cells), so the stream is the connection.

## How it works

**The two units.** Both composites have a pervious and an impervious surface, each draining through its own internal reach, and three soil layers (thicknesses D/7, 2D/7 and 4D/7, D being the depth to groundwater) under the pervious surface. In the output, member names carry the unit name as a prefix, for example `Riparian__Near_Stream_Aquifer_piezometric_head`.

| | Upland (Mixed HRU) | Riparian (Riparian Urban HRU) |
|---|---|---|
| Area A, impervious fraction f_i | 80 ha, 0.15 | 20 ha, 0.10 |
| Impervious / pervious surface | 12 ha / 68 ha | 2 ha / 18 ha |
| Soil layers | 0.5, 1.0, 2.0 m | 0.24, 0.49, 0.97 m |
| Soil (all layers) | K_sat 0.5 m/day, α 1.5 1/m, n 1.4, θ_sat 0.42, θ_res 0.06 | same |
| Groundwater | one `Groundwater cell`, 68 ha, porosity 0.25 | regional `Unconfined Groundwater cell`, 15 ha, S_y 0.2, plus near-stream aquifer, 5 ha, S_y 0.25 |
| Recharge | constant conductivity 0.05 m/day | unsaturated conductivity of `Soil_3` |
| Initial water table | 103.0 m (3.5 m below the soil column) | 98.3 m (at the base of the soil column) |

**Surfaces and channels.** Each surface drains to its reach by sheet flow, Q = 86400·(W/n)·S^0.5·max(d − d_s, 0)^(5/3) in m³/day, with width W, slope S, roughness n, ponded depth d and depression storage d_s. The internal reaches, the two stream segments and the links between them use Manning's equation driven by the head difference between neighboring segments, Q = 86400·(1/n̄)·A_u·R^(2/3)·((h_1 − h_2)/L̄)^0.5. Infiltration, percolation between soil layers and evapotranspiration (E = 0.8·ET₀·A_1·θ_1/θ_sat) are as in the other HRUs.

**Upland groundwater.** The Mixed HRU uses the stock `Groundwater cell`, with head h = base + b + (θ_g − φ)/S_s. Setting S_s = φ/b = 0.031 1/m (b = 8 m) makes this the height of a free water table. Recharge is Q_r = A_p·K_r·(h_3 − h_g)/L with K_r = 0.05 m/day. The cell discharges to the upper stream through `Upland_baseflow`, Q = A_b·K·(h_g − h_stream)/L.

**Riparian groundwater.** The riparian unit splits its aquifer in two:

- The **regional cell** (area A·(1 − f_r) = 15 ha, f_r = 0.25 being the near-stream fraction) receives recharge from `Soil_3` over 13.5 ha. It drains into the near-stream aquifer through the internal `hillslope_to_near_stream` link,
  Q = c · ½(K_r + K_n) · ½(b_r + b_n) · W · (h_r − h_n)/L
  with W = 2000 m (both sides of the 1000 m stream), L = 100 m (the hillslope length), K the cells' conductivities (2 and 5 m/day), b their saturated thicknesses and c a cutoff that stops the outflow as the upgradient cell approaches its residual thickness.
- The **near-stream aquifer** (A·f_r = 5 ha) receives recharge over 4.5 ha and exchanges water with the lower stream through `Bank_exchange`, Q = K·A_b·(h_n − h_stream)/L_b. Because the path is short (12.5 m), it responds within hours and in both directions.

Both cells are unconfined, with head h = base + V/(S_y·area). Recharge into them uses the unsaturated conductivity of the bottom soil layer,

  Q_r = A_r·K_sat,3·[k_r(S_e,3)·(h_3 − h_g)⁺ − (h_g − h_3)⁺]/L,  L = (d_3 + b)/2

so it can also run upward when the water table rises above the soil head.

## What to look for in the results

- **Storm runoff is impervious runoff.** The pervious surfaces produce almost no runoff (rain never exceeds their infiltration capacity). The upland impervious surface delivers 17,600 m³ (99% of the rain on it) and the riparian impervious surface 2,900 m³. The outlet peaks at 25,400 m³/day (0.29 m³/s) on day 7.7.
- **The corridor adds baseflow.** Between storms only 60 to 70 m³/day of upland baseflow enters the corridor, but the outlet carries 330 to 390 m³/day. The difference is the near-stream aquifer discharging to the lower stream. Over the month the bank exchange delivers 8,500 m³, more than the riparian runoff and four times the upland baseflow (2,000 m³).
- **Bank storage.** In every storm the lower stream rises by up to 0.23 m and the bank exchange falls (from about 350 to 115 m³/day on day 2.3). In the largest storm (day 7.7) it reverses: for about four hours the stream loses up to 98 m³/day to its banks. The water returns over the following days. The upland baseflow dips in the same way when the upper stream rises.
- **Two time scales.** The near-stream water table stays within 0.12 m of its start because the stream controls it. The regional water table rises 0.19 m with recharge, and its drainage into the near-stream aquifer grows from 0 to 150 m³/day. This slow store sustains the near-stream discharge between storms.
- **Water balance (30 days, 100 ha):**

| Term | m³ | mm over 100 ha |
|---|---|---|
| Rain | 148,672 | 148.7 |
| Evapotranspiration | −36,685 | −36.7 |
| Outflow at the outlet | −31,299 | −31.3 |
| Increase in upland soil water | 27,238 | 27.2 |
| Increase in upland groundwater | 43,942 | 43.9 |
| Increase in riparian soil water | 4,737 | 4.7 |
| Increase in riparian groundwater | 4,741 | 4.7 |
| Increase in surface, reach and stream storage | 15 | 0.0 |

The residual is 16 m³ (0.01% of the rain).

## Assumptions and limitations

- The upland groundwater cell of the Mixed HRU has the pervious area only (68 ha), not the whole unit. Per unit of recharge its water table therefore rises 1/(1 − f_i) = 1.18 times faster than an aquifer under the whole unit would. The Urban and Riparian HRUs give the aquifer the whole area.
- The upland recharge uses a constant conductivity. With the water table 3.5 m below the soil column this makes recharge only weakly dependent on soil moisture, and the first days show the drainage of the initial soil water.
- The upland groundwater cannot flow into the riparian aquifer: the two units use different groundwater cell types and no port connects them. Upland groundwater reaches the corridor only as baseflow in the stream.
- Each unit is laterally uniform. The riparian near-stream aquifer is one cell for both banks.
- The model starts from assumed initial states and runs for one month, so the groundwater stores are still adjusting at the end. A longer spin-up would be needed for a study.
- There is no evapotranspiration from the riparian groundwater, although riparian vegetation often draws on it (the Urban HRU has an optional source for this; the Riparian HRU does not).
