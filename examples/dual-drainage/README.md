---
title: Urban Dual Drainage (Street and Storm Sewer)
track: storm
level: 3
status: ready
doc: hydrologic_response_units.pdf
summary: A 40 ha urban neighbourhood drains to a street, grate inlets take the street flow into a 0.6 m storm sewer, and whatever the sewer cannot carry runs overland to the stream. A moderate storm stays in the pipe; an intense one surcharges the sewer and floods the street.
plugins: [dual_drainage, urban_hru, compound_channel, Sewer_system, open_channel, unconfined_groundwater, unsaturated_soil, soil_evapotranspiration_models]
features: [Minor and major systems, Grate inlets (HEC-22), Sewer surcharge, Urban HRU composite, Overland overflow]
keywords: [dual drainage, minor system, major system, street flow, gutter, inlet, grate inlet, hec-22, storm sewer, surcharge, manhole, outfall, flooding, urban flooding, urban drainage, compound channel, urban hru, impervious, dcia, baseflow]
components:
  Rain: "Rainfall applied to both surfaces of the neighbourhood: two storms, 10 mm/h for 3 h starting at day 1.0 (30 mm) and 50 mm/h for 1 h starting at day 3.5 (50 mm)."
  ET: "Soil evapotranspiration source: 0.8 × reference ET (about 2.4 mm/day) × θ/θ_s, withdrawn from the top soil layer of the pervious area."
  Neighbourhood: "An Urban_HRU composite of 40 ha, 30 % directly connected impervious. It contains a pervious and an impervious surface, an internal reach for each, three van Genuchten soil layers (0.5, 1.0 and 2.0 m thick) under the pervious part and an unconfined groundwater cell. Its two surface outlets discharge into the street; its groundwater discharges into the stream."
  Street: "The surface (major) drainage system: 800 m of street modelled as a Compound Channel Segment. A triangular gutter (A = 2·y², 0.15 m deep, 0.6 m wide at the curb top) carries small flows; above 0.15 m the water spreads over a 10 m wide road surface with 20:1 sides. Gutter invert at 95 m."
  Storm_Sewer: "The underground (minor) drainage system: an 800 m, 0.6 m diameter trunk sewer (Manning n = 0.013) with its invert at 93 m and crown at 93.6 m. When full, its head rises 0.11 m per m³ of extra storage, which represents water rising in the manholes."
  Stream: "The receiving stream: 600 m long, main channel A = 6·y^1.5 up to 0.6 m deep, then a 10 m floodplain with 10:1 sides. Bed at 90 m."
  Outlet: "Fixed-head boundary at 89 m, 1 m below the stream bed, so the stream discharges freely."
  Pervious_outlet: "Reach_link port of the composite: Manning flow from the internal reach of the pervious surface into the street."
  Impervious_outlet: "Impervious_Reach_link port: Manning flow from the internal reach of the impervious surface (roofs, roads, parking) into the street. This carries almost all storm runoff."
  Baseflow: "Darcy exchange between the neighbourhood groundwater and the stream, Q = K·A·(h_gw − H_stream)/L with K = 5 m/day, A = 6000 m², L = 150 m. Positive from the aquifer to the stream; it reverses when the stream rises above the water table."
  Inlets: "All grate inlets along the street lumped into one Swale_to_pipe_inlet link: 20 m of weir length, 1.5 m² of opening, inlet elevation 95 m. Positive from the street into the sewer; negative when a surcharged sewer overflows back onto the street."
  Outfall: "Pipe_outfall_link from the sewer into the stream, invert 91 m. Manning flow with the sewer's flowing area over half the sewer length. Positive into the stream."
  Overland_overflow: "Compound_Channel_link from the street directly to the stream: the overland (major system) path taken by street flow that does not enter the inlets."
  Stream_outlet: "channel2fixed link: Manning outflow from the stream to the fixed-head outlet."
inputs:
  rainfall.csv: "Hourly rainfall, days 0 to 6. Three columns, no header: interval start (day), interval end (day), rain depth in the interval (m). OpenHydroQual divides the depth by the interval length to get the intensity (m/day). Synthetic."
  reference_et.csv: "Daily reference evapotranspiration, two columns, no header: time (day), ET rate (m/day), about 2.4 mm/day. Synthetic."
plots:
  - title: Rainfall
    ylabel: Intensity (m/day)
    series:
      - {column: "Rain_Intensity", label: "Rain intensity"}
    caption: "Storm 1 (day 1.0 to 1.125) at 0.24 m/day (10 mm/h) and storm 2 (day 3.5 to 3.54) at 1.2 m/day (50 mm/h)."
  - title: Where the street runoff goes
    ylabel: Flow (m³/day)
    series:
      - {column: "Impervious_outlet_flow", label: "Runoff into the street"}
      - {column: "Inlets_flow", label: "Inlets (street to sewer)"}
      - {column: "Outfall_flow", label: "Sewer outfall"}
      - {column: "Overland_overflow_flow", label: "Overland overflow"}
      - {column: "Stream_outlet_flow", label: "Stream outflow"}
    caption: "In storm 1 the inlets take all the street runoff (peak 28,800 m³/day, 0.33 m³/s) and nothing flows overland. In storm 2 the street receives 131,000 m³/day (1.5 m³/s); the sewer is capped near 56,000 m³/day (0.65 m³/s) and about 50,000 m³/day (0.58 m³/s) runs overland."
  - title: Water levels in the street and the sewer
    ylabel: Hydraulic head (m)
    series:
      - {column: "Street_head", label: "Street water surface"}
      - {column: "Storm_Sewer_head", label: "Sewer head"}
    caption: "The gutter invert and the inlets are at 95 m and the sewer crown at 93.6 m. In storm 2 the sewer surcharges and its head climbs to 95.16 m, above the inlets but below the street water surface (95.24 m), so water keeps entering the sewer and never flows back out."
  - title: Groundwater exchange with the stream
    ylabel: Flow (m³/day)
    series:
      - {column: "Baseflow_flow", label: "Baseflow (aquifer to stream)"}
    caption: "Baseflow grows slowly as recharge raises the water table, and briefly reverses in storm 2 when the stream stage rises above the water table."
---

## What this model represents

In most developed areas, runoff from roofs, roads and parking lots does not reach a stream through an open channel. It runs along street gutters to grate inlets, drops into a storm sewer, and is discharged at an outfall into the nearest stream. This underground network is the **minor system**. It is designed for frequent storms (typically a 2 to 10 year return period). When a storm exceeds the capacity of the inlets or of the pipe, the excess stays on the street and flows overland, along the street and through low points, to the receiving water: the **major system**. A model that represents both, and lets water move between them, is a **dual drainage** model.

This example is a single 40 ha neighbourhood served by one street and one trunk sewer, subjected to two storms: a moderate one that the sewer handles completely and an intense one that it does not. It shows how to

- connect an `Urban_HRU` composite (surfaces, soils and groundwater in one object) to a street in place of a stream,
- represent the inlets with the HEC-22 weir and orifice relations,
- let the sewer surcharge into its manholes, and
- route the flow the sewer cannot take overland to the stream.

The same building blocks scale up: a city is many such units, each with its own street and sewer segment, with the sewer segments connected to each other.

## How it works

**Flow path.** Rain falls on the neighbourhood. The impervious surface (30 %, 12 ha) drains through its internal reach and `Impervious_outlet` into the `Street`. The pervious surface (28 ha) infiltrates into the soil column; any surface runoff drains through `Pervious_outlet`, also into the street. From the street, water either enters the `Storm_Sewer` through the `Inlets` or flows along the street surface directly to the `Stream` (`Overland_overflow`). The sewer discharges into the stream through the `Outfall`. Water that infiltrates percolates through the three soil layers, recharges the groundwater, and returns to the stream as `Baseflow`. The stream drains to a fixed-head `Outlet`.

All flows are in m³/day and are positive in the direction of the link (`from` to `to`).

**The neighbourhood (Urban_HRU).** The composite places its members from three numbers: the ground surface z_s = 100 m, the depth to groundwater D = 3.5 m and the groundwater thickness b = 12 m. The soil layers are D/7, 2D/7 and 4D/7 thick (0.5, 1.0 and 2.0 m) and cover the pervious area A(1 − f_i) = 280,000 m². The groundwater cell lies beneath the soil column (base at 84.5 m) and covers the whole 400,000 m². Each surface drains to its internal reach by kinematic sheet flow (`Catchment_link`):

  Q = 86400 · (W/n) · S^½ · (d − d_s)₊^(5/3)

with W = 4000 m, S = 0.03, n = 0.15 (pervious) or 0.015 (impervious), and depression storage d_s = 5 mm (pervious) or 1.5 mm (impervious). The reaches drain to the street by Manning's equation (`Reach_link`, `Impervious_Reach_link`). Infiltration, percolation and recharge use van Genuchten and Mualem relations; the details are in the technical guide linked above.

**Street.** A `Compound Channel Segment` whose cross-sectional area is

  A = a·y^m for y ≤ y_b,  A = a·y_b^m + (T_b + w_f)·(y − y_b) + s·(y − y_b)² for y > y_b

with a = 2, m = 2, bank depth y_b = 0.15 m, bank top width T_b = a·m·y_b^(m−1) = 0.6 m, flat width w_f = 10 m and side slope s = 20. The gutter holds 0.045 m² per metre of street; above that the water spreads across the road. Depth is computed from storage by inverting this relation, and head = depth + 95 m.

**Inlets.** All inlets on the street are lumped into one grate inlet with the two regimes of FHWA HEC-22, weir flow at shallow depth and orifice flow once submerged, whichever is smaller:

  Δh = max(H_street, z_in) − max(H_sewer, z_in)
  Q_w = C_w · P · |Δh|^1.5 · |Δh| / (|Δh| + h_s)
  Q_o = C_d · A_in · √(2g·|Δh|)
  Q = 86400 · sign(Δh) · min(Q_w, Q_o)

with z_in = 95 m, C_w = 1.66, P = 20 m, C_d = 0.67, A_in = 1.5 m² and h_s = 5 mm. The two regimes cross at Δh ≈ 0.13 m, so the inlets work as a weir in both storms. The factor |Δh|/(|Δh| + h_s) only smooths the flow near zero depth (it is above 0.9 for Δh > 45 mm). Water enters the sewer while the sewer head is below the street water surface. If the sewer head rises above it, Δh changes sign and the sewer overflows onto the street (`one_way = 0` allows this). When both heads are below the inlets, Δh = 0 and nothing flows.

**Sewer.** A `Sewerchannelsegment` of diameter D_p = 0.6 m and length L = 800 m. The normalized flowing area V/(L·D_p²) gives the normalized depth through a fitted polynomial (capped at 1), and the flowing area and wetted perimeter follow from the depth through polynomial fits for a circular section. Once the pipe is full (V > π/4·D_p²·L = 226 m³), the head rises by the surcharge coefficient c_s for every cubic metre stored in excess:

  H_sewer = 93 + y + c_s · (V − π/4·D_p²·L)₊

c_s = 0.11 m/m³ corresponds to 1.2 m diameter manholes every 100 m (1/(1.13 m² × 8 manholes)): the surcharged water rises in the manholes. A finite c_s also keeps the solver well behaved; a nearly rigid pipe (the default 10,000 m/m³) makes the system stiff.

**Outfall.** Manning flow from the centre of the sewer to its outlet, over half its length:

  Q = 86400 · (1/n) · sign(Δh)·√(|Δh|/(L/2)) · A_s · (A_s/P_s)^(2/3),  Δh = max(H_sewer, z_out) − max(H_stream, z_out)

with z_out = 91 m and A_s, P_s the flowing area and wetted perimeter of the sewer. (OpenHydroQual uses a slightly regularized signed square root.) Because the sewer centre sits 2 m above the outfall invert, the pipe has a driving gradient of about 0.5 % even when it carries little water. The full-pipe capacity is about 0.5 m³/s; surcharge adds head and raises it to about 0.65 m³/s. The stream never rises to 91 m in this run, so the outfall is always free.

**Overland overflow and stream.** `Overland_overflow`, `Stream_outlet` and the reach outlets are Manning connectors, Q = 86400 · (1/n̄) · A · R^(2/3) · √(Δh/L̄). For `Overland_overflow`, A is the flowing area of the street (the end with the higher head), R uses the mean wetted perimeter of street and stream, n̄ = (0.03 + 0.04)/2 and L̄ = (800 + 600)/2 m. This link is always present, but while the water stays in the gutter its flowing area is tiny, so it carries almost nothing. Once the street floods above the curb, both area and hydraulic radius grow quickly and the link becomes the main escape path.

**Time step.** `max_timestep_increase_factor = 1` holds every step at the initial 0.001 day (86 s), so the one-hour storms and the fast street and sewer response are resolved finely. The run takes about 8 seconds.

**Groundwater and baseflow.** The unconfined groundwater head is h_g = z_g + V_g/(S_y·A) with S_y = 0.15. Recharge from the bottom soil layer uses the unsaturated conductivity of that layer, so it declines as the soil drains. `Baseflow` is Q = K·A_b·(h_g − H_stream)/L_b = 200 m²/day × (h_g − H_stream). The water table starts at 90.3 m, 0.3 m above the stream bed.

## What to look for in the results

- **Storm 1 stays in the minor system.** 10 mm/h on 12 ha of impervious surface delivers a peak of 28,800 m³/day (0.33 m³/s) to the street. The gutter fills to 5 cm, the inlets pass all of it, the sewer runs 62 % full (normalized depth 0.62) and the outfall hydrograph almost coincides with the inlet hydrograph. Overland overflow peaks at 17 m³/day, practically nothing.
- **Storm 2 exceeds the sewer.** At 50 mm/h the street receives 131,000 m³/day (1.5 m³/s). The inlets briefly take 67,000 m³/day (0.78 m³/s) while the empty pipe fills, then the sewer surcharges and its throughput is capped by the outfall at about 56,000 m³/day (0.65 m³/s). The street floods to 0.235 m, over the curb and across the road, and about 50,000 m³/day (0.58 m³/s) flows overland to the stream.
- **Surcharge without reverse flow.** For about 1.5 hours the sewer is surcharged. Its head reaches 95.16 m, 1.56 m above the pipe crown and 0.16 m above the inlets: water has risen in the manholes to street level. The street surface (95.24 m) stays higher, so Δh across the inlets stays positive and the sewer never spills back onto the street. A larger storm, a smaller outfall or a high stream (backwater at the outfall) would reverse the inlet flow.
- **Volume split.** Of the 6,000 m³ that fell on impervious surfaces in storm 2, about 4,300 m³ went through the sewer and 1,700 m³ over the street. In storm 1, all 3,400 m³ went through the sewer.
- **The pervious area produces almost no runoff.** The infiltration capacity of the top layer is larger than both rain intensities, so the 28 ha of lawns and gardens absorb both storms (about 22,000 m³ in total). That water reaches the stream only slowly, through recharge and baseflow.
- **Bank storage.** During storm 2 the stream rises to 0.5 m deep, above the water table, and the baseflow reverses (down to −24 m³/day) for about an hour: the stream loses water to the aquifer.

## Assumptions and limitations

- One lumped inlet per street segment. The travel time along the gutter to each inlet and the bypass of inlets at high gutter velocity (inlet efficiency) are not represented.
- One sewer segment represents the trunk; the storage and travel time of the branch network are lumped into it.
- The sewer cannot be filled from the stream through the outfall (reverse outfall flow uses the sewer's current flowing area), so backwater from a high stream is underestimated.
- The overland path goes straight from the street to the stream; ponding in low spots, buildings and flow across private property are not represented.
- The connected impervious fraction (30 %) is taken as given. Impervious surfaces that drain onto lawns belong to the pervious area.
- Storms and evapotranspiration are synthetic. The initial soil moisture and water table are not in equilibrium, which is why recharge declines and baseflow rises steadily through the run.
