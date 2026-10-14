---
title: Culvert Verification Suite
track: hyd
level: 2
status: ready
model: T4_roadway_overtopping.ohq
doc: culvert_model.pdf
summary: A road culvert between two channel reaches, hit by an extreme storm that overtops the road. Ten companion models cover inlet and outlet control, submergence, rising tailwater, box barrels, reverse flow and tracer transport.
plugins: [culvert, open_channel]
features: [HDS-5 inlet control, Outlet control, Roadway overtopping, Surcharged barrel, Verification set]
keywords: [culvert, road crossing, inlet control, outlet control, hds-5, fhwa, headwater, tailwater, hw/d, roadway overtopping, broad-crested weir, submerged inlet, surcharge, preissmann slot, box culvert, multi-barrel, reverse flow, entrance loss, exit loss, verification]
extra_files: [T1_inlet_control.ohq, T2_submerged_inlet.ohq, T3_outlet_control_tailwater.ohq, T5_box_multibarrel.ohq, T6_reverse_flow.ohq, T7_lumped_vs_routed.ohq, T8_dry_to_dry.ohq, T9_steep_slope.ohq, T10_water_quality.ohq, T11_outlet_control_hgl.ohq, inflow_moderate.csv, inflow_large.csv, inflow_small.csv, inflow_pulse.csv, tailwater_rise.csv, surge.csv, tracer_in.csv]
components:
  US_Channel: Upstream (headwater) channel reach, 100 m long, trapezoidal with a 3 m base width, side slopes of 2 horizontal to 1 vertical, Manning n = 0.035 and bed at 0.5 m. The storm hydrograph enters here. Its water level is the culvert headwater.
  Barrel: One circular concrete pipe, 1.0 m diameter and 20 m long, inverts at 0.5 m (inlet) and 0.3 m (outlet), n = 0.013. A storage block, so it can fill, run full and surcharge.
  DS_Channel: Downstream (tailwater) channel reach, same cross-section as the upstream reach, bed at 0.3 m.
  Outfall: Fixed water level of 0.35 m at the end of the downstream reach, 5 cm above its bed, so in practice a free outfall.
  Inlet: Entrance of the culvert. Passes the smaller of the HDS-5 inlet-control capacity and the entrance-loss limited flow (k_e = 0.5). Coefficients are for a circular concrete pipe, square edge with headwall.
  Outlet: Exit of the culvert. Barrel friction plus exit loss (k_x = 1.0), with the HDS-5 (d_c + D)/2 tailwater rule applied when the barrel is deep.
  Tailwater: Manning flow from the downstream reach to the outfall level.
  Road: The road embankment over the culvert, crest at 2.3 m and 12 m long, acting as a broad-crested weir from the upstream to the downstream reach.
inputs:
  inflow_extreme.csv: "Inflow to the upstream reach of the main model (T4): a Gaussian storm peaking at 9.0 m³/s at t = 0.5 day on a 0.02 m³/s base flow. Time in days, flow in m³/day, every 0.005 day. Synthetic. Also used by T5."
  inflow_moderate.csv: Same shape, 0.8 m³/s peak (T1, T3, T9, T10). Time in days, flow in m³/day.
  inflow_large.csv: Same shape, 3.2 m³/s peak (T2, T7, T11). Time in days, flow in m³/day.
  inflow_small.csv: Small storm, 0.1 m³/s peak at t = 0.3 day on a 0.01 m³/s base flow (T6). Time in days, flow in m³/day.
  inflow_pulse.csv: Square pulse of 1.2 m³/s from t = 0.2 to 0.5 day, zero otherwise (T8). Time in days, flow in m³/day.
  tailwater_rise.csv: Outfall water level (m) rising from 0.35 m to 1.90 m and back, peak at t = 0.55 day (T3). Time in days.
  surge.csv: Outfall water level (m) with a sharp surge from 0.35 m to 2.55 m at t = 1.0 day (T6). Time in days.
  tracer_in.csv: Tracer concentration in the upstream inflow (g/m³), 50 g/m³ from t = 0.30 to 0.45 day, zero otherwise (T10). Time in days.
  T1_inlet_control.ohq: Companion model T1 (see the table of test cases).
  T2_submerged_inlet.ohq: Companion model T2.
  T3_outlet_control_tailwater.ohq: Companion model T3.
  T5_box_multibarrel.ohq: Companion model T5.
  T6_reverse_flow.ohq: Companion model T6.
  T7_lumped_vs_routed.ohq: Companion model T7.
  T8_dry_to_dry.ohq: Companion model T8.
  T9_steep_slope.ohq: Companion model T9.
  T10_water_quality.ohq: Companion model T10.
  T11_outlet_control_hgl.ohq: Companion model T11.
plots:
  - title: Where the flood goes
    ylabel: Flow (m³/day)
    series:
      - {column: "US_Channel_inflow", label: "Storm inflow"}
      - {column: "Inlet_flow", label: "Through the culvert"}
      - {column: "Road_flow", label: "Over the road"}
      - {column: "Tailwater_flow", label: "Leaving the downstream reach"}
    caption: The culvert caps at about 2.7 m³/s (237,000 m³/day). Above that the road overtops and carries 6.3 m³/s at the peak, about half of the storm volume.
  - title: Water levels
    ylabel: Elevation (m)
    series:
      - {column: "US_Channel_head", label: "Headwater (upstream reach)"}
      - {column: "Barrel_head", label: "Barrel"}
      - {column: "DS_Channel_head", label: "Tailwater (downstream reach)"}
    caption: The headwater rises to 2.76 m, 0.46 m above the 2.3 m road crest. The barrel surcharges by up to 0.72 m above its crown. The tailwater stays low, so the culvert stays in inlet control.
  - title: Inlet regime
    ylabel: Dimensionless
    series:
      - {column: "Inlet_hw_ratio", label: "HW/D"}
      - {column: "Inlet_submergence_weight", label: "Weight of the submerged form"}
    caption: The inlet moves from the unsubmerged to the submerged HDS-5 equation (weight 0 to 1) as HW/D passes 1.15 to 1.30, and back on the falling limb.
---

## What this model represents

A road crosses a small stream on an embankment, and the stream passes under the road through a single 1.0 m concrete pipe culvert. Every culvert analysis asks the same questions: for a given flood, how high does the water rise upstream (the headwater), which part of the structure limits the flow, and does the road overtop?

The main model (`T4_roadway_overtopping.ohq`) answers these for an extreme storm with a 9 m³/s peak, about three times the pipe's capacity. The download also contains ten smaller companion models, T1 to T11, each of which isolates one culvert behavior. Together they form the verification set for the culvert components. They are listed in the table below and documented in the technical guide (PDF).

## How it works

The crossing is built from three objects in series, plus a road link in parallel:

  US_Channel → **Inlet** → **Barrel** → **Outlet** → DS_Channel → Tailwater → Outfall
  US_Channel → **Road** → DS_Channel

**Channel reaches.** Each trapezoidal reach is one storage cell. Its depth follows from storage S, length L, base width b and side slope z:

  d = (−b + √(b² + 4·z·S/L)) / (2·z),  head h = z_bed + d

**Barrel.** The barrel is also a storage cell. The wetted fraction u = S/S_full, with S_full = N·L·πD²/4, gives the depth through a polynomial fit to the circular section. Once the barrel runs full, extra volume is stored in a narrow virtual slot above the crown (a Preissmann slot of width σ·D, σ = `slot_width_ratio` = 0.05), which converts pressure head into a stage:

  h = (z_inlet + z_outlet)/2 + d(u) + max(S − S_full, 0) / (N·L·σ·D)

The barrel friction loss coefficient is f = 2g·n²·L / R^(4/3), with R the hydraulic radius of the wetted section.

**Inlet link (inlet control).** HDS-5 expresses inlet control through the discharge parameter q* = K_u·Q / (A·D^0.5), with K_u = 1.811 in SI units. With HW the headwater depth above the inlet invert and S₀ the barrel slope:

- Unsubmerged (Form 1): HW/D = H_c/D + K·q*^M − 0.5·S₀, where H_c is the specific head at critical depth. The link solves it for q* with four fixed-point iterations through the critical-flow function of the circular section.
- Submerged: HW/D = c·q*² + Y − 0.5·S₀, so q* = √((HW/D − Y + 0.5·S₀)/c).
- The two forms are blended by a weight that ramps from 0 to 1 as the submerged q* goes from 3.5 to 4.0, which bridges the gap HDS-5 leaves between them.

The inlet link then passes

  Q = min(Q_inlet, |Q_entrance|) · sign(Q_entrance),  Q_inlet = N·q*·A·D^0.5 / K_u,  Q_entrance = N·A·√(2g·Δh / k_e)

where Δh is the head difference between the upstream reach and the barrel (each floored at the inlet invert) and A is the full barrel area. Here K = 0.0098, M = 2.0, c = 0.0398, Y = 0.67 (HDS-5 Table A.1, circular concrete, square edge with headwall) and k_e = 0.5.

**Outlet link (outlet control).** Between the barrel and the downstream reach:

  Q = A·√(2g·(h_barrel − TW) / (k_x + f))

with k_x = 1.0. When the barrel is deep (barrel head above the outlet invert between 0.75·D and 1.8·D), the tailwater TW is progressively raised to at least the HDS-5 grade line z_outlet + (d_c + D)/2, where d_c is the critical depth at the current flow. This represents outlet control with a low tailwater.

Because the entrance loss (k_e) and the barrel and exit losses (k_x + f) sit on two links with the barrel storage between them, the steady-state result equals the single HDS-5 outlet-control equation HW = TW + (k_e + k_x + f)·V²/2g.

**Road link.** Flow over the embankment is a broad-crested weir:

  Q_road = k_t·C_r·B·[max(h_up − z_crest, 0)^1.5 − max(h_down − z_crest, 0)^1.5]

with C_r = 1.7 (SI), B = 12 m, z_crest = 2.3 m and k_t = 1 (no submergence correction).

**Sign convention.** All links are positive from upstream to downstream. Negative values mean reverse flow, which T6 exercises.

**Units.** Flows in the model and in the output are in m³/day (1 m³/s = 86,400 m³/day), lengths in m, time in days.

### The test cases

Every case except T7 and T10 uses the same reaches, barrel and links as the main model, without the road link. The results below come from running each model with the current OpenHydroQual release. "Closure" is the volume balance over the structure (inflow − outflow − change in storage) as a fraction of the inflow volume.

| Case | Model file | Condition | What it verifies | Result |
|---|---|---|---|---|
| T1 | `T1_inlet_control.ohq` | 0.8 m³/s storm, free outfall | Unsubmerged inlet control (HDS-5 Form 1) | HW/D peaks at 0.75; the submerged weight stays 0; inlet control governs throughout |
| T2 | `T2_submerged_inlet.ohq` | 3.2 m³/s storm | Submerged inlet, barrel surcharge through the slot | HW/D 2.78, q* 7.3; the barrel surcharges about 1.0 m above the crown |
| T3 | `T3_outlet_control_tailwater.ohq` | 0.8 m³/s storm, outfall level rising to 1.9 m | Switch from inlet to outlet control as the tailwater drowns the outlet | Inlet control governs about 60% of the time, outlet control the rest |
| T4 | `T4_roadway_overtopping.ohq` (main) | 9.0 m³/s storm, road crest 2.3 m | Roadway overtopping in parallel with a surcharged culvert | 0.46 m over the crest, 6.3 m³/s over the road, 51% of the storm volume |
| T5 | `T5_box_multibarrel.ohq` | 9.0 m³/s storm, three 1.5 m × 1.2 m box cells | Box section, multiple barrels, box inlet coefficients (K = 0.026, M = 1.0, c = 0.0347, Y = 0.81) | Carries the full 9.0 m³/s with HW/rise 0.99 |
| T6 | `T6_reverse_flow.ohq` | Small storm, then an outfall surge to 2.55 m | Flow reversal through the outlet and inlet | Flow reverses to −0.093 m³/s; the barrel surcharges 1.15 m |
| T7 | `T7_lumped_vs_routed.ohq` | 3.2 m³/s storm, two independent crossings | Single-link `Circular Culvert` versus the storage-routed barrel | Peak flows and volumes agree to better than 0.01% |
| T8 | `T8_dry_to_dry.ohq` | 1.2 m³/s square pulse, 3 days | Wetting from dry and full drain-down | Returns to dry with no negative storage; closure 0.002% |
| T9 | `T9_steep_slope.ohq` | 0.8 m³/s storm, 5% barrel slope | Steep barrel, strong inlet control | Inlet control throughout; barrel depth never above 43% of the diameter |
| T10 | `T10_water_quality.ohq` | 0.8 m³/s storm with a 50 g/m³ tracer pulse | Constituent transport through the inlet, barrel and outlet | Peak concentration 50.0 g/m³ upstream and in the barrel, 49.6 g/m³ downstream |
| T11 | `T11_outlet_control_hgl.ohq` | 3.2 m³/s storm, 60 m corrugated barrel (n = 0.024) on a 0.17% slope | The (d_c + D)/2 grade line rule | Rule active on 57% of flowing steps; the effective tailwater rises from 0.52 m to 1.37 m |

Volume closure is better than 0.02% for every case except T6 (0.26%), where a sharp surge arrives against a nearly empty barrel. All models cap the solver time step at 0.0025 day (3.6 minutes) through `max_timestep_increase_factor`. With the default cap of 0.025 day the steps are too coarse to follow the boundary time series, and the volume balance of T3 degrades to about 1.8%.

## What to look for in the results

- **The inlet caps the culvert flow.** The culvert flow levels off near 2.7 m³/s while the inflow keeps rising to 9 m³/s. At the peak, HW/D = 2.26 and the submerged inlet equation gives q* = √((2.26 − 0.67 + 0.005)/0.0398) = 6.3, so Q = 6.3 × 0.785 m² × (1 m)^0.5 / 1.811 = 2.74 m³/s, which matches the output.
- **Overtopping from t = 0.33 to 0.68 day.** At the peak the headwater is 2.76 m, 0.46 m above the crest, and the weir carries 1.7 × 12 × 0.456^1.5 = 6.28 m³/s. Over the event, 51% of the volume crosses the road.
- **The road limits the headwater.** Although the inflow is three times the pipe capacity, the headwater rises only 0.46 m above the crest, because weir capacity grows with the 1.5 power of head.
- **Surcharge.** The barrel stage rises above its crown (mean invert 0.4 m plus 1.0 m) by up to 0.72 m, through the Preissmann slot.
- **Inlet control throughout.** The downstream reach stays below 1.24 m, so the outlet never limits the flow. The regime plot shows the switch to the submerged inlet form and back.
- **Little attenuation.** The two reaches store only a few hundred cubic meters, so the outflow hydrograph closely follows the inflow.

## Assumptions and limitations

- Each reach and the barrel are single storage cells. There is no water-surface profile in the barrel (no M1, M2 or S2 curves, no hydraulic jump), and on steep slopes the barrel depth comes from its volume, not from normal depth.
- The fit for the wetted perimeter of a circular barrel is about 5% low at full flow, which raises the friction-controlled capacity by about 3%. Inlet control is not affected.
- The (d_c + D)/2 rule is ramped in between 0.75 and 1.8 barrel rises, a wider band than HDS-5 implies, for numerical robustness.
- The Preissmann slot is a numerical device. It slightly inflates stored volume once the barrel surcharges.
- The roadway weir uses a constant coefficient and no tailwater submergence correction (k_t = 1). In T4 the downstream reach never reaches the crest, so this has no effect here.
- The downstream boundary is a fixed level. A real downstream channel would raise its stage with flow, which pushes a culvert toward outlet control (as T3 shows).
- All hydrographs are synthetic.
