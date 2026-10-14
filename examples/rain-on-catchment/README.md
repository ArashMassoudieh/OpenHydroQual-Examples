---
title: Rain on a Catchment
track: start
level: 1
status: ready
summary: A paved 1.2 ha catchment receives 36 days of hourly rainfall and drains through a Manning-type outlet to a fixed-head boundary. The smallest complete rainfall-runoff model.
plugins: [main_components]
features: [Blocks and links, Precipitation source, Rainfall time series, Water balance]
keywords: [first model, rainfall, runoff, precipitation, catchment, outlet, hydrograph, manning, overland flow, sheet flow, nonlinear reservoir, runoff coefficient, impervious, parking lot, time series, water balance, beginner]
components:
  Rainfall: Hourly rainfall depths read from `rainfall.csv`. Any block that names this source as its precipitation receives the intensity multiplied by the block's area.
  Catchment: A 12,000 m² (1.2 ha) paved surface, 100 m wide and 120 m long in the flow direction, with a 0.5% slope and Manning's n of 0.015 (smooth asphalt). 90% of the rain becomes runoff; the other 10% is treated as lost (wetting, small depressions, evaporation).
  Outlet: The drainage point of the catchment, for example a storm drain inlet. A fixed-head boundary at 0 m that accepts any flow without filling up.
  Runoff: Sheet flow leaving the catchment, computed from Manning's equation with the catchment's ponded water depth. Always directed from Catchment to Outlet.
inputs:
  rainfall.csv: "Hourly rainfall. Three columns, comma separated, no header: interval start (days), interval end (days), rainfall depth in that interval (mm). Day 0 is 10 August 2011 at 00:00; the record covers 36 days (864 hourly intervals, 381.8 mm in total). Extracted from the sample rain gauge record distributed with the OpenHydroQual tutorials."
plots:
  - title: Effective rainfall and runoff
    ylabel: Flow rate (m³/day)
    series:
      - {column: "Catchment_Precipitation_runoff", label: "Effective rainfall onto the catchment"}
      - {column: "Runoff_flow", label: "Runoff to the outlet"}
    caption: Runoff follows the rainfall within minutes. Peaks are set by the most intense hour of a storm, not by its total depth.
  - title: Ponded water depth on the catchment
    ylabel: Depth (m)
    series:
      - {column: "Catchment_depth", label: "Catchment depth"}
    caption: The sheet of water on the pavement never exceeds about 5 mm and drains away within a few hours after rain stops.
---

## What this model represents

A small paved area, such as a parking lot or a commercial block, that sheds rainfall to a single storm drain inlet. It is the smallest complete rainfall-runoff model in OpenHydroQual: one **source** (the rainfall record), one **block** that stores water (the catchment surface), one **link** (the overland flow that leaves it) and one **boundary block** (the outlet).

The rainfall record is 36 days of hourly data from late summer 2011. It contains a moderate storm on day 4, a short, very intense storm on day 9, a long storm of 85 mm on day 17 and a wet spell from day 26 to day 30. This mix shows how a fast-responding surface reacts to storms of different intensity and duration.

## How it works

**Rainfall input.** Each row of `rainfall.csv` gives a time interval and the rain depth that fell in it. OpenHydroQual converts each row to an average intensity, i = depth / (end − start), in m/day (the `[mm]` unit tag on the file name converts millimetres to metres). Intensities are placed at the middle of each interval and interpolated linearly between them, so the file should use intervals of equal length, as this one does. The rainfall delivered to a block is

  P = i · A

where A is the block's area (m²). For this catchment, 1 mm/h corresponds to 288 m³/day.

**Catchment water balance.** The catchment stores water as a thin sheet with depth d = S / A, where S is the stored volume (m³). Its balance is

  dS/dt = C_r · P − Q

where C_r is the runoff coefficient (0.9 here) and Q is the outflow through the **Runoff** link. The remaining fraction, (1 − C_r) · P, is reported as `Precipitation_loss` and never enters the storage. Evapotranspiration, external inflow and a first-order loss term (`loss_coefficient` · S) are available on the Catchment block but are not used here.

**Outflow.** The Runoff link is a `Catchment_link`, which applies Manning's equation to a wide, shallow sheet of flow:

  Q = 86400 · (W / n) · s^0.5 · max(d − d_s, 0)^(5/3)

with width W = 100 m, Manning's n = 0.015, slope s = 0.005 and depression storage d_s = 0 m. The factor 86400 converts m³/s to m³/day. Because Q grows with depth to the power 5/3, the catchment behaves as a nonlinear reservoir: a deeper sheet drains much faster than a shallow one. Only the catchment's own depth enters the equation, so the outlet cannot back water up onto the catchment.

**Outlet.** The Outlet is a `fixed_head` block. Its head and storage are held constant, so it absorbs any flow it receives. Its only role is to give the runoff somewhere to go.

## What to look for in the results

- **Fast response.** Runoff peaks within about 15 minutes of the rainfall peak. With a 5.3 mm sheet, Q ≈ 6,600 m³/day and S ≈ 64 m³, so the catchment's characteristic response time, S / ((5/3)·Q), is about 8 minutes. A paved surface of this size provides almost no attenuation at hourly resolution.
- **Peak flow follows intensity, not storm total.** The storm on day 9 (41 mm, with 31 mm in its wettest hour) produces the largest runoff peak, about 6,600 m³/day. The day 17 storm deposits twice as much rain (85 mm) but more steadily, never exceeding about 10 mm/h, and its runoff peak is less than half as large.
- **Small depths.** The ponded depth stays below about 5 mm. After each storm it recedes over a few hours. Because Q ∝ d^(5/3), the tail of the recession is slow: a fraction of a millimetre remains for a day or more.
- **Water balance.** 381.8 mm over 1.2 ha is 4,581 m³ of rain. With C_r = 0.9, 4,123 m³ enters the catchment storage, and essentially all of it has reached the outlet by the end of the run.

## Assumptions and limitations

- The catchment is a single, uniform storage. There is no routing along the flow path, so the hydrograph shape comes only from the nonlinear storage-outflow relation.
- Losses are a fixed fraction of rainfall (the runoff coefficient). There is no infiltration capacity, no initial abstraction and no evaporation between storms. Pervious catchments are better represented with the soil or curve-number examples.
- Rainfall is uniform over the catchment and known at hourly resolution. Within each hour the intensity is interpolated linearly, so bursts shorter than an hour are smoothed.
- The outlet is a free boundary: tailwater in the drain does not affect the runoff.
