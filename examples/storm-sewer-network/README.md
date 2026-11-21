---
title: Storm Sewer Network with Modified Rational Method Catchments
track: storm
level: 2
status: ready
summary: Four small urban catchments (Catchment MRM blocks) drain through catch basins into a branched storm sewer that discharges to a creek. A 2-year storm passes through the pipes; a 100-year storm surcharges them, floods three manholes onto the street, and the ponded water drains back after the rain.
plugins: [Sewer_system]
features: [Modified Rational Method catchments, Branched sewer network, Pipe surcharge, Street flooding at catch basins, Design storm vs extreme storm]
keywords: [storm sewer, sewer network, rational method, modified rational method, mrm, runoff coefficient, time of concentration, catch basin, manhole, surcharge, hydraulic grade line, manning, pipe capacity, street flooding, ponding, design storm, 2-year storm, 100-year storm, urban drainage, outfall, nonlinear reservoir]
components:
  Rain: "Rainfall applied to all four catchments: a 1-hour block of 30.5 mm/h (1.2 in/hr, a 2-year storm) from hour 0 to 1, and a 1-hour block of 76.2 mm/h (3.0 in/hr, a 100-year storm) from hour 6 to 7."
  Catchment_A: "Residential catchment, 2.02 ha (5 ac), runoff coefficient C = 0.6, flow path 152.4 m (500 ft), slope 0.02. Drains to MH_A at the head of the first lateral."
  Catchment_B: "Residential catchment, 1.62 ha (4 ac), C = 0.6, flow path 121.9 m (400 ft), slope 0.02. Drains to MH_B at the head of the second lateral."
  Catchment_C: "Commercial catchment, 1.01 ha (2.5 ac), C = 0.9, flow path 79.2 m (260 ft), slope 0.01. Drains to MH_C, where the two laterals meet."
  Catchment_D: "Mixed commercial catchment, 1.62 ha (4 ac), C = 0.8, flow path 100.6 m (330 ft), slope 0.01. Drains to MH_D on the trunk."
  MH_A: "Catch basin (manhole) at the head of lateral P1: 0.93 m² (10 ft²) base, invert 3.048 m (10 ft), 1.83 m (6 ft) deep to the rim. Above the rim the water spreads on the street (side slope 50)."
  MH_B: "Catch basin at the head of lateral P2: same size, invert 2.941 m (9.65 ft)."
  MH_C: "Junction catch basin where P1 and P2 meet and P3 starts: invert 2.377 m (7.8 ft)."
  MH_D: "Catch basin on the trunk, upstream of the outfall pipe: invert 1.524 m (5.0 ft)."
  Creek: "Fixed-head boundary for the receiving creek, water level 0.762 m (2.5 ft), below the outfall invert, so the sewer discharges freely."
  Runoff_A: "Catchment outlet (MRM) link from Catchment_A to MH_A. All four Runoff links follow the same outlet equation (see How it works)."
  Runoff_B: "Catchment outlet (MRM) link from Catchment_B to MH_B."
  Runoff_C: "Catchment outlet (MRM) link from Catchment_C to MH_C."
  Runoff_D: "Catchment outlet (MRM) link from Catchment_D to MH_D."
  P1: "Lateral sewer pipe MH_A to MH_C: 0.381 m (15 in) diameter, 121.9 m (400 ft) long, inverts 3.048 to 2.438 m (slope 0.005), Manning n = 0.013."
  P2: "Lateral sewer pipe MH_B to MH_C: 0.381 m (15 in), 100.6 m (330 ft), slope 0.005, n = 0.013."
  P3: "Trunk sewer pipe MH_C to MH_D: 0.533 m (21 in), 152.4 m (500 ft), slope 0.005, n = 0.013."
  P4: "Outfall pipe MH_D to Creek: 0.610 m (24 in), 100.6 m (330 ft), slope 0.005, n = 0.013."
inputs:
  rainfall.csv: "Rain depth per 1-minute interval over 12 hours. Three columns, no header: interval start (day), interval end (day), depth in the interval (m). 0.508 mm per minute from hour 0 to 1 and 1.27 mm per minute from hour 6 to 7, zero otherwise. Synthetic design storms."
plots:
  - title: Rainfall
    ylabel: Intensity (mm/h)
    series:
      - {column: "Rain_Intensity", label: "Rain intensity", scale: 41.6667}
    caption: "The 2-year storm (30.5 mm/h) in the first hour and the 100-year storm (76.2 mm/h) from hour 6 to 7."
  - title: Runoff from the catchments
    ylabel: Flow (m³/s)
    series:
      - {column: "Runoff_A_flow", label: "Catchment A", scale: 1.157407e-5}
      - {column: "Runoff_B_flow", label: "Catchment B", scale: 1.157407e-5}
      - {column: "Runoff_C_flow", label: "Catchment C", scale: 1.157407e-5}
      - {column: "Runoff_D_flow", label: "Catchment D", scale: 1.157407e-5}
    caption: "Each catchment levels off at C·i·A while the rain lasts (A: 0.103 m³/s in the 2-year storm, 0.257 m³/s in the 100-year storm) and reaches it faster in the heavier storm."
  - title: Water film on catchment A
    ylabel: Depth (mm)
    series:
      - {column: "Catchment_A_depth", label: "Catchment A", scale: 1000}
    caption: "The film thickens until the outlet discharges C·i·A: 2.78 mm in the 2-year storm and 4.33 mm in the 100-year storm, the depths given by the outlet equation."
  - title: Flow in the sewer pipes
    ylabel: Flow (m³/s)
    series:
      - {column: "P1_flow", label: "P1 (lateral from A)", scale: 1.157407e-5}
      - {column: "P2_flow", label: "P2 (lateral from B)", scale: 1.157407e-5}
      - {column: "P3_flow", label: "P3 (trunk)", scale: 1.157407e-5}
      - {column: "P4_flow", label: "P4 (outfall)", scale: 1.157407e-5}
    caption: "In the 2-year storm the pipe flows are the sums of C·i·A upstream (P4: 0.372 m³/s). In the 100-year storm every pipe surcharges; P4 peaks at 0.788 m³/s, well below the 0.929 m³/s of runoff, because water is held on the street."
  - title: Water depth in the manholes
    ylabel: Depth (m)
    series:
      - {column: "MH_A_depth", label: "MH_A"}
      - {column: "MH_B_depth", label: "MH_B"}
      - {column: "MH_C_depth", label: "MH_C"}
      - {column: "MH_D_depth", label: "MH_D"}
    hlines: [{y: 1.8288, label: "Rim (1.83 m above the invert)"}]
    caption: "In the 2-year storm the manholes hold 0.23 to 0.35 m of water. In the 100-year storm MH_A, MH_B and MH_C rise above the rim; MH_D, near the outfall, does not."
  - title: Water ponded on the street
    ylabel: Volume (m³)
    series:
      - {column: "MH_A_flood_volume", label: "MH_A"}
      - {column: "MH_B_flood_volume", label: "MH_B"}
      - {column: "MH_C_flood_volume", label: "MH_C"}
    caption: "Only the 100-year storm floods the street: up to 285 m³ at MH_A, 135 m³ at MH_B and 13 m³ at MH_C. All of it drains back into the sewer within about 30 minutes of the end of the rain."
---

## What this model represents

A small urban storm sewer: four catchments (two residential, two commercial, 6.27 ha in total) drain through catch basins into a branched pipe network. Two 0.381 m (15 in) laterals start at manholes MH_A and MH_B and meet at MH_C; a 0.533 m (21 in) trunk carries the water to MH_D, and a 0.610 m (24 in) outfall pipe discharges to a creek. The pipes were sized with the Rational method for a 2-year storm of 30.5 mm/h (1.2 in/hr), each running about 80 % of its full-pipe capacity.

The same 12-hour run first applies that 2-year storm and then, six hours later, a 100-year storm of 76.2 mm/h (3.0 in/hr). The first passes through the pipes. The second surcharges them: water rises in the manholes, spills over three of the rims, ponds on the street, and drains back once the rain stops. The example shows how the Catchment (MRM) block reproduces the Rational method, how pipe capacity limits a sewer, and where a network floods first. The model is the one built in the OpenHydroQual video tutorial on storm sewer networks (designed in US customary units; the US values are given in parentheses).

## How it works

**Catchment (MRM) blocks: a nonlinear reservoir.** Each catchment stores a thin film of water on its surface, with depth d = Storage/A (A is the catchment area). The precipitation source adds the rain over the area; the block keeps the fraction C (the runoff coefficient) and removes the rest as a loss:

  effective inflow = C·i·A,  loss = (1 − C)·i·A

where i is the rain intensity. The Catchment outlet (MRM) link drains the film (flow in m³/day, lengths in m):

  Q = (A / L) · γ · S^0.28 · (d − d_s)^(1+m),  γ = (1440/0.31)^(1+m)

with L the flow path length, S the slope, d_s the depression storage (0 here) and m = 1.07 the nonlinearity exponent, so the outflow grows with the film depth to the power 2.07. The storage changes as dStorage/dt = C·i·A − Q. During a storm longer than the catchment's response time the film thickens until Q = C·i·A, which is the Rational method peak. Setting the two equal gives the equilibrium film depth

  d = (C·i·A·L / (A·γ·S^0.28))^(1/2.07)

The time to approach it plays the role of the time of concentration. It is longer for a long, flat catchment, and shorter for heavier rain, because a deeper film drains faster: catchment A reaches 95 % of C·i·A after 21 minutes in the 2-year storm and after 13.5 minutes in the 100-year storm.

**Catch basins.** A Catch basin stores water over its base area A_b up to its rim height h_r (Storage/A_b below the rim). Above the rim the excess spreads over the street as an inverted square pyramid with side slope s: the flooded area beyond the basin is (√A_b + 2·s·h_f)² − A_b for a flood depth h_f above the rim. The hydraulic head is the bottom elevation plus the depth, and it drives the pipes.

**Sewer pipes.** The Sewer pipe link computes Manning flow between two heads (flow in m³/day):

  Q = 86400 · (1/n) · √(Δh/L) · A_eff · R^(2/3),  Δh = max(H_s, z_s) − max(H_e, z_e)

where H_s and H_e are the heads at the upstream and downstream manholes, z_s and z_e the pipe inverts, and L the pipe length. The flow depth at each end is the head above the invert, capped at the diameter; the flowing area and wetted perimeter come from polynomial fits of the circular section, weighted toward the upstream end. With a free outfall Δh is the upstream depth plus the drop in invert. When the pipe flows full, A_eff = πD²/4 and Δh is the difference in hydraulic grade line between the manholes, which can exceed the pipe slope times its length: a surcharged pipe carries more than its full-pipe capacity on its own slope.

**Network.** Each catchment outlet enters its catch basin; the pipes connect the basins, and P4 ends at the fixed-head Creek, which sits below the outfall invert. Flows are positive in the drawn direction (upstream to downstream); a pipe reverses only if the downstream head rises above the upstream one.

## What to look for in the results

- **Rational method.** In the 2-year storm each catchment levels off at C·i·A: Catchment_A at 0.6 × 30.5 mm/h × 2.02 ha = 0.103 m³/s (3.63 cfs). The pipe flows are the sums upstream: P3 carries 0.262 m³/s (A + B + C) and P4 0.372 m³/s (13.1 cfs), matching i·ΣCA.
- **Film depth.** Catchment A holds 2.78 mm (0.110 in) of water at equilibrium in the 2-year storm and 4.33 mm (0.171 in) in the 100-year storm, the depths given by the equilibrium equation above.
- **Pipe capacity.** Full-pipe Manning capacity on the 0.005 slope is 0.129 m³/s (4.57 cfs) for the 0.381 m laterals, 0.317 m³/s for P3 and 0.453 m³/s for P4. The 2-year flows use about 80 % of it; the pipes run about two-thirds full.
- **Surcharge.** In the 100-year storm Catchment_A delivers 0.257 m³/s to MH_A, twice what P1 can carry on its slope. The water rises in MH_A until the head difference to MH_C drives about 0.165 m³/s through the full pipe, and the rest rises over the rim.
- **Street flooding.** MH_A floods 0.43 m (17 in) above the rim with up to 285 m³ (10,100 ft³) on the street, about the 100-year runoff minus the pipe flow integrated over the hour of rain. MH_B and MH_C flood less, and MH_D does not flood. After the rain, MH_C drains first, the head difference across P1 grows, and P1 briefly carries more than during the storm while the street empties.
- **Water balance.** The volume through the outfall equals the runoff (C × rain × area) of both storms to within about 1 %.

## Assumptions and limitations

- Runoff is a fixed fraction C of the rain: there is no infiltration model, no initial abstraction and no depression storage.
- Each catchment is one reservoir with uniform rain; there is no gutter or overland routing between catchments, and ponded street water stays at its own catch basin (it does not flow along the street to the next one; see the Dual Drainage example for that).
- Pipes carry no storage of their own (the catch basins hold the water), and inertia is neglected: the pipe flow follows Manning's equation on the head difference at every step. Entrance and exit losses at the manholes are not modeled.
- The circular-section area and wetted perimeter come from polynomial fits; at full flow the fitted wetted perimeter is about 2.99·D, slightly less than π·D, so the full-pipe flow is about 3 % higher than the exact Manning value.
- The creek level is fixed and below the outfall, so there is no tailwater effect.
- Rain depths in rainfall.csv are in meters, the default unit of a precipitation file. A file in other units can be used by choosing its unit (for example `in`) for the source's time series before loading it; the model file then stores it as `timeseries=rain.csv [in]`. The video version of this model uses storm files in inches.
