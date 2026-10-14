---
title: Reservoir Operation Rule
track: hyd
level: 2
status: ready
summary: A water-supply reservoir passes a year of inflows. Releases follow a storage-based operating rule with a minimum environmental flow, a linear conservation zone and a maximum outlet capacity, and a spillway takes the excess in floods.
plugins: [Reservoir_operation, main_components]
features: [Rule-based release, Storage zones, Spillway rating, Annual simulation]
keywords: [reservoir, dam, reservoir operation, operating rule, release rule, rule curve, storage zones, conservation pool, flood control pool, dead storage, minimum release, environmental flow, outlet works, spillway, storage-discharge, water supply, flood control, drought]
components:
  Reservoir: A storage reservoir with a volume of 6 million m³ at the start of the year. It is described by its stored volume only (no elevation or surface area). Receives the inflow from `reservoir_inflow.csv`.
  Downstream_River: The river below the dam. A boundary that receives both releases. Its storage is the cumulative volume released.
  Outlet_Works: The controlled release (gates or valves in the outlet works). Release follows the operating rule with S_min = 4 million m³, S_max = 16 million m³, Q_min = 1 m³/s (86,400 m³/day) and Q_max = 15 m³/s (1,296,000 m³/day).
  Spillway: Uncontrolled overflow represented by a steep power-law rating in storage, Q = c·S^12. Negligible at normal storage, it grows quickly once the reservoir rises above S_max.
inputs:
  reservoir_inflow.csv: "Inflow to the reservoir over one year. A seasonal base flow between 0.5 and 5.5 m³/s (highest around day 120) plus six storm events with peaks of 25, 60, 35, 20, 8 and 12 m³/s on days 95, 120, 140, 175, 250 and 300, each with a one-day rise and a 4-day exponential recession. Time in days, flow in m³/day, every 0.25 day. Synthetic."
plots:
  - title: Storage
    ylabel: Storage (m³)
    series:
      - {column: "Reservoir_Storage", label: "Reservoir storage"}
    caption: Storage rises above S_max = 16 million m³ during the wet-season storms (days 121 to 129 and 142 to 146) and falls below S_min = 4 million m³ late in the dry season (days 284 to 300 and 333 to 346).
  - title: Inflow and releases
    ylabel: Flow (m³/day)
    series:
      - {column: "Reservoir_inflow", label: "Inflow"}
      - {column: "Outlet_Works_flow", label: "Outlet works release"}
      - {column: "Spillway_flow", label: "Spillway"}
    caption: The release follows storage, not inflow. It holds at Q_max (1.30 million m³/day) while the reservoir is above S_max, and at Q_min (86,400 m³/day) while it is below S_min. The spillway only matters during the largest storm.
---

## What this model represents

A dam stores water in the wet season and releases it through the year for water supply and to keep a minimum flow in the river downstream. The operator divides the reservoir volume into zones and sets the release according to which zone the storage is in. This is the simplest form of a reservoir operating rule (a rule curve), and it is how many planning models represent reservoir operation.

The model follows one reservoir through a synthetic year with a wet season around day 120 and a long dry season afterwards. It shows how a rule tied to storage attenuates floods, carries water over into the dry season, and protects a minimum release when inflows are low.

## How it works

**Reservoir.** The reservoir is a single storage S (m³) with the mass balance

  dS/dt = Q_in(t) − Q_release − Q_spill

where Q_in is read from `reservoir_inflow.csv`.

**Outlet works (operating rule).** The release depends only on the current storage, in three zones:

| Zone | Storage | Release |
|---|---|---|
| Below the conservation zone | S < S_min | Q_min |
| Conservation zone | S_min < S < S_max | Q_min + (S − S_min)/(S_max − S_min) · (Q_max − Q_min) |
| Flood zone | S > S_max | Q_max |

With S_min = 4 × 10⁶ m³, S_max = 16 × 10⁶ m³, Q_min = 1 m³/s and Q_max = 15 m³/s, the release in the conservation zone rises by 1.17 m³/s for every million m³ of storage. Q_min plays the role of an environmental or downstream supply release. Q_max is the capacity of the outlet works. The release is reduced automatically only if the reservoir is about to empty, so that storage cannot become negative.

**Spillway.** The spillway link uses a power-law rating in storage:

  Q_spill = c · S^p,  c = 8.44 × 10⁻⁸², p = 12

with S in m³ and Q in m³/day. The coefficient is chosen so that Q_spill = 40 m³/s at S = 20 million m³. With an exponent this high the rating acts like an overflow crest: it passes less than 0.001 m³/s at 8 million m³, 2.8 m³/s at S_max, and grows rapidly above that. The link has no explicit crest, so it is never exactly zero.

**Downstream river.** Both links discharge to a fixed-level boundary. Neither link depends on the water level downstream, so the boundary only collects the released volume.

**Sign convention and units.** Both links are positive from the reservoir to the river. Flows are in m³/day (1 m³/s = 86,400 m³/day), storage in m³, time in days.

## What to look for in the results

- **Start of the year.** At 6 million m³ the rule releases 3.3 m³/s, more than the 1.8 m³/s inflow, so storage first drops to about 5.2 million m³ (day 15) before the rising base flow brings it back up.
- **Flood attenuation.** The largest storm brings 63 m³/s at day 120. Storage climbs above S_max on day 121 and peaks at 18.4 million m³ on day 123. The outlet works release their maximum of 15 m³/s and the spillway adds up to 15 m³/s, so the peak outflow is 30 m³/s, about half of the peak inflow. Storage is in the flood zone from day 121 to 129 and again from day 142 to 146, after the third storm.
- **Conservation zone.** Between the storms the release follows storage along the straight line of the rule, so it falls gradually as the reservoir drains and keeps the downstream river well above the minimum.
- **Dry season.** From day 284 to 300, and again from day 333 to 346, storage is below S_min = 4 million m³ and the release is held at Q_min = 1 m³/s, more than the inflow (as low as 0.51 m³/s). The minimum release continues to draw the reservoir down, to a low of 3.44 million m³ on day 299. The small storms on days 250 and 300 lift the storage only briefly.
- **Annual balance.** Over the year 157 million m³ flows in, 149 million m³ leaves through the outlet works and 9.4 million m³ over the spillway, and storage ends 1.6 million m³ lower than it started.

## Assumptions and limitations

- The reservoir has no stage-storage-area relationship, so there is no reservoir water level and no evaporation, seepage or direct rainfall on the water surface.
- The rule depends on storage only. Real rule curves usually change with the season (a lower flood-zone limit in the wet season, for example) and may also depend on forecasts or downstream conditions, which this link does not represent.
- The release changes instantly with storage. Real gate operation happens in discrete steps.
- The spillway rating is a smooth power law in storage, not a weir equation with a crest elevation. Its parameters were chosen for this illustration.
- Downstream water levels do not affect either release.
- The inflow series is synthetic.
