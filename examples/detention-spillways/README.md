---
title: Detention Pond with Riser and Emergency Spillway
track: storm
level: 2
status: ready
summary: A dry detention pond with a low-flow orifice, a drop-inlet riser and an emergency spillway routes two synthetic storm hydrographs. The small storm is handled by the orifice and the riser weir; the large one drives the riser into pipe control and spills over the emergency spillway.
plugins: [dam_spillways, Pond_Plugin]
features: [Level-pool routing, Low-flow orifice, Riser weir and conduit control, Emergency spillway, Peak attenuation]
keywords: [detention, dry pond, detention basin, stormwater pond, riser, drop inlet, principal spillway, spillway, emergency spillway, auxiliary spillway, broad-crested weir, orifice, outlet structure, stage-storage, stage-discharge, peak flow, attenuation, flood routing, level pool routing, design storm, unit hydrograph, scs, dam]
components:
  Detention_Pond: "A dry pond with its floor at 100.0 m. Storage follows S = 1600·d² (d = water depth, m), so the water surface area is 3,200·d m²: 3,200 m² at 1 m depth and 7,680 m² at 2.4 m. Empty at the start. Receives the inflow hydrograph from `inflow.csv`."
  Downstream_Channel: "Receiving channel, a fixed-head boundary at 100.125 m (the centre of the low-flow orifice). Its storage only accumulates the outflow volume."
  Low_Flow_Orifice: "A 0.25 m diameter orifice (0.0491 m²) at the pond floor with discharge coefficient 0.6. It releases water at any depth above its centre and drains the pond between storms."
  Riser: "Drop-inlet principal spillway: a riser with a 3 m crest perimeter at 101.5 m (1.5 m above the floor), discharging through a 0.6 m conduit whose outlet is at 99.5 m (total loss coefficient 1.5). Flow is the smaller of the riser weir capacity and the conduit capacity."
  Emergency_Spillway: "A 10 m wide broad-crested auxiliary spillway with its crest at 102.2 m (2.2 m above the floor), weir coefficient 1.7 m^0.5/s. It operates only in floods that the riser cannot pass."
inputs:
  inflow.csv: "Synthetic inflow hydrograph: time (day), inflow (m³/day), at 5-minute spacing. Two SCS-type (gamma-shaped) hydrographs with a 45-minute time to peak: a 2.0 m³/s peak starting at 6 h (7,200 m³) and a 5.0 m³/s peak starting at 36 h (18,000 m³)."
plots:
  - title: Inflow and outflow through each outlet
    ylabel: Flow (m³/day)
    series:
      - {column: "Detention_Pond_inflow", label: "Inflow"}
      - {column: "Low_Flow_Orifice_flow", label: "Low-flow orifice"}
      - {column: "Riser_flow", label: "Riser"}
      - {column: "Emergency_Spillway_flow", label: "Emergency spillway"}
    caption: "The first storm passes through the orifice and the riser weir only. In the second, the riser flattens at its conduit capacity (1.35 m³/s = 116,600 m³/day) and the emergency spillway takes the excess near the peak."
  - title: Pond water level
    ylabel: Water surface elevation (m)
    series:
      - {column: "Detention_Pond_head", label: "Pond level"}
    caption: The level rises above the riser crest (101.5 m) in both storms and above the emergency spillway crest (102.2 m) only in the second. Between and after the storms the orifice draws the pond down to its centre (100.125 m).
  - title: Stored volume
    ylabel: Storage (m³)
    series:
      - {column: "Detention_Pond_Storage", label: "Pond storage"}
    caption: Storage peaks at about 4,800 m³ in the first storm and 9,200 m³ in the second, at the moment the total outflow equals the inflow.
---

## What this model represents

A dry detention pond reduces the peak flow from a developed catchment by storing runoff temporarily and releasing it through an outlet structure. A typical structure, modelled here, has three outlets:

- a **low-flow orifice** at the floor, which releases small flows and empties the pond after each storm,
- a **riser** (drop inlet), a vertical pipe whose rim acts as a weir and which discharges through a conduit under the embankment (the principal spillway),
- an **emergency spillway**, a wide overflow section in the embankment that protects the dam when a flood exceeds what the riser can pass.

The pond routes two synthetic storms, a moderate one and a large one, so that every outlet and both riser control regimes (weir and pipe) come into play. This is the classic "level-pool routing" problem of pond design, solved here as a continuous simulation.

## How it works

**Storage.** The pond is a `Pond` block. Its volume S (m³) changes with the inflow and the three outflows:

  dS/dt = Q_in(t) − Q_orifice − Q_riser − Q_emergency

The stage-storage relation is a power law, S = α·d^β, with α = 1600 and β = 2. OpenHydroQual computes the depth as d = [S²/(α·(S + 0.1))]^(1/β), which equals (S/α)^(1/β) except within a fraction of a cubic metre of empty. The water level is H = 100.0 m + d, and the surface area α·β·d^(β−1) = 3,200·d m² grows linearly with depth, as in a basin with sloping sides.

**Low-flow orifice** (`orifice` link from `Pond_Plugin`):

  Q_orifice = 86400 · C · A_o · [19.6 · (H − H_down)]₊^0.5  (m³/day)

with C = 0.6 (the `head_loss_coefficient` property acts as a discharge coefficient), A_o = 0.0491 m² and H_down the head of `Downstream_Channel`. The downstream head is set to the orifice centre (100.125 m), so the driving head is measured to the orifice centroid, as for an orifice discharging freely.

**Riser** (`Riser_Spillway` link from `dam_spillways`):

  Q_riser = min( 86400 · C_w · L · (H − z_c)₊^1.5 ,  86400 · (π/4) · D² · [2g · (H − z_out)₊ / (1 + K)]^0.5 )

The first term is the weir capacity of the riser rim (C_w = 1.84 m^0.5/s, crest perimeter L = 3 m, crest z_c = 101.5 m). The second is the capacity of the conduit flowing full under the head between the pond level and the conduit outlet (D = 0.6 m, z_out = 99.5 m, total loss coefficient K = 1.5). At low heads over the crest the weir controls. The two capacities are equal at H = 101.87 m (1.87 m depth); above that level the conduit controls and the riser flow grows only with the square root of the head. The outlet discharges freely, so the downstream level does not affect it.

**Emergency spillway** (`Emergency_Spillway` link):

  Q_emergency = a · (H − z_e)₊^1.5

with crest z_e = 102.2 m and a = 1,468,800 m^1.5/day, which is 86400 × 1.7 m^0.5/s × 10 m: a broad-crested weir 10 m wide.

All three links flow only from the pond to the channel; none of them can reverse.

**Inflow.** `inflow.csv` holds two hydrographs with the shape of the SCS dimensionless unit hydrograph (gamma form):

  q(t) = q_p · [(t′/t_p) · e^(1 − t′/t_p)]^3.7

where t′ is the time since the start of the event and t_p = 45 min. The events start at 6 h (q_p = 2.0 m³/s) and 36 h (q_p = 5.0 m³/s).

**Time stepping.** The inflow changes from zero to its peak in under an hour. With the default setting, only precipitation series limit the time step, and the solver can step across a short hydrograph peak. The model therefore sets `timestep_clamp_series` to "All time series" and limits the step to 5 times the initial step (0.005 day, about 7 minutes).

## What to look for in the results

| | Storm 1 | Storm 2 |
|---|---|---|
| Inflow peak | 2.0 m³/s at 6.7 h | 5.0 m³/s at 36.7 h |
| Total outflow peak | 0.81 m³/s at 7.4 h | 3.08 m³/s at 37.2 h |
| Peak reduction | 59% | 38% |
| Maximum depth | 1.74 m | 2.40 m |
| Maximum storage | 4,840 m³ | 9,230 m³ |
| Riser control at peak | weir (0.64 m³/s) | conduit (1.35 m³/s) |
| Emergency spillway peak | none | 1.54 m³/s |

- **Peak attenuation and lag.** The outflow peaks about 30 to 40 minutes after the inflow, exactly when the pond level peaks. At that moment inflow and outflow are equal, which is the defining property of level-pool routing.
- **Outlet staging.** Below 1.5 m depth only the orifice releases water, at up to about 0.15 m³/s. The riser starts when the level passes 101.5 m, and the emergency spillway only when it passes 102.2 m.
- **Riser in pipe control.** In storm 2 the riser flow levels off at 1.35 m³/s while the pond keeps rising. Once the conduit controls, the extra head over the crest buys little extra capacity, which is why an emergency spillway is needed.
- **Emergency spillway.** It flows for about 56 minutes (36.9 to 37.8 h) and passes 2,860 m³, 16% of the storm 2 volume.
- **Drawdown.** After each storm the orifice empties the pond to its centre level in about 12 to 13 hours. The pond is effectively empty when storm 2 arrives, so the two events do not interact.
- **Volume balance.** Of the 25,190 m³ of inflow, the orifice releases 10,690 m³, the riser 11,560 m³ and the emergency spillway 2,860 m³. The 25 m³ below the orifice centre remains in the pond at the end.

## Assumptions and limitations

- Level-pool (storage) routing: the pond surface is assumed flat, with no travel time across it.
- The stage-storage relation is a single power law. A real pond would use a surveyed stage-storage table, and the β exponent can be fitted to one.
- The rating equations use constant coefficients. Riser crest submergence, orifice control at the riser inlet, vortices and partly full conduit flow are not represented.
- The orifice equation has no invert. Using the orifice centre as the downstream head reproduces free discharge, but it leaves 25 m³ below that level that never drains, and it would not be correct if the channel level rose above the orifice.
- The emergency spillway discharges freely: tailwater, erosion of the spillway and overtopping of the embankment are not modelled.
- There is no rainfall on the pond surface, evaporation or infiltration through the pond floor.
- The inflow hydrographs are synthetic. In a design study they would come from a rainfall-runoff model of the catchment for the design storms required by the local standard.
