---
title: 'SCS Curve Number: Design Storm'
track: hydro
level: 1
status: ready
doc: curve_number_method.pdf
summary: A rural and an urban sub-watershed in series respond to a 75 mm, 6-hour design storm. Runoff volume follows the NRCS Curve Number equation and is routed through a Nash cascade timed by the NRCS lag. A third catchment compares the 5-reservoir and 3-reservoir cascades.
plugins: [cn_catchment]
features: [Curve Number runoff, NRCS lag routing, Nash cascade, Chained sub-watersheds, Composite catchments]
keywords: [curve number, scs, nrcs, cn, tr-55, tr-20, design storm, hyetograph, runoff, rainfall excess, initial abstraction, retention, unit hydrograph, nash cascade, linear reservoir, lag time, watershed, hydrograph, peak flow, urbanization]
components:
  Design_storm: 'The design storm: 75 mm of rain in 6 hours, peaking at 31 mm/h between hours 2.50 and 2.75, followed by 30 hours without rain. Applied uniformly to all three catchments.'
  Rural: An upstream rural sub-watershed of 1 km² (100 ha) with CN = 65, a 2000 m longest flow path and 3% slope. Uses the 5-reservoir cascade (`CN_Catchment`). Its outlet hydrograph discharges into the surface reservoir of `Urban`.
  Urban: A downstream urban sub-watershed of 0.4 km² (40 ha) with CN = 90, an 800 m flow path and 1% slope. It generates its own runoff and also routes the inflow from `Rural` through its cascade to the watershed outlet.
  Rural_3res: A copy of `Rural` that uses the 3-reservoir cascade (`CN_Catchment_3`). It is not connected to the rest of the watershed and exists only so that the two cascade lengths can be compared on one plot.
  Watershed_outlet: Fixed-head boundary that receives the combined hydrograph. Its storage starts at zero, so it accumulates the total runoff volume leaving the watershed.
  Comparison_outlet: Fixed-head boundary for the comparison catchment. Its storage accumulates the runoff volume of `Rural_3res`.
  Rural_runoff: Outlet hydrograph of `Rural` (discharge of its fifth reservoir), delivered to the surface reservoir of `Urban`.
  Watershed_hydrograph: Outlet hydrograph of `Urban`, which carries the urban runoff plus the routed rural runoff. This is the watershed hydrograph.
  Rural_3res_hydrograph: Outlet hydrograph of `Rural_3res` (discharge of its third reservoir).
inputs:
  design_storm.csv: 'Rainfall depth per interval. Three columns, no header: interval start (days), interval end (days), depth that fell in the interval (m). 144 intervals of 15 minutes over 1.5 days; total depth 0.075 m.'
plots:
  - title: Design storm
    ylabel: Rainfall intensity (m/day)
    series:
      - {column: "Design_storm_Intensity", label: "Intensity"}
    caption: The hyetograph. 0.75 m/day is 31 mm/h. All rain falls in the first 6 hours.
  - title: Outlet hydrographs
    ylabel: Flow (m³/day)
    series:
      - {column: "Rural_runoff_flow", label: "Rural, 5 reservoirs"}
      - {column: "Rural_3res_hydrograph_flow", label: "Rural, 3 reservoirs"}
      - {column: "Watershed_hydrograph_flow", label: "Watershed outlet (urban + routed rural)"}
    caption: The urban catchment responds first and sets the watershed peak. The rural runoff arrives later and forms the raised falling limb. The 3-reservoir cascade gives a lower, broader rural peak with the same volume.
  - title: Runoff fraction
    ylabel: C (–)
    series:
      - {column: "Rural__Retention_C", label: "Rural (CN 65)"}
      - {column: "Urban__Retention_C", label: "Urban (CN 90)"}
    caption: The share of the instantaneous rainfall that becomes runoff. It stays at zero until the initial abstraction is filled, then rises with cumulative rain. After the storm it falls slowly as the abstraction store recovers.
  - title: Cumulative runoff volume
    ylabel: Volume (m³)
    series:
      - {column: "Watershed_outlet_Storage", label: "Watershed outlet"}
      - {column: "Comparison_outlet_Storage", label: "Comparison outlet (rural, 3 reservoirs)"}
    caption: Total runoff volumes. The final values (32,000 m³ and 12,300 m³) match the Curve Number equation to within 0.1%.
---

## What this model represents

This model applies the classical NRCS (formerly SCS) Curve Number method to a small two-part watershed during a single design storm. An upstream **rural** sub-watershed (100 ha, CN 65, for example pasture and woodland on moderately permeable soil) drains through a downstream **urban** sub-watershed (40 ha, CN 90, a densely developed area). The urban outlet is the watershed outlet. A third catchment, **Rural_3res**, repeats the rural parameters with a shorter routing cascade, so that the effect of hydrograph shape can be seen on its own.

The Curve Number method is the standard tool for design-storm runoff in small watersheds (TR-55, TR-20, HEC-HMS). The model shows how OpenHydroQual turns this event method into a continuous simulation and how a watershed is built by chaining catchments.

## How it works

Each catchment is a composite block. `CN_Catchment` contains one abstraction store (`Retention`) and five linear reservoirs (`R1` to `R5`). `CN_Catchment_3` is identical except that it has three reservoirs. Rain falls on the surface reservoir `R1`. Members appear in the output with the catchment name as a prefix, for example `Rural__Retention_C` or `Urban__R1_Storage`.

**Retention and runoff fraction.** The Curve Number sets the maximum retention S and the initial abstraction Ia (both in m):

  S = 25.4/CN − 0.254,  Ia = 0.2·S

which gives S = 136.8 mm and Ia = 27.4 mm for the rural catchments, and S = 28.2 mm and Ia = 5.6 mm for the urban one. The `Retention` member stores the abstracted volume V_W. Its depth W = V_W/A sets the instantaneous runoff fraction

  C = max(1 − ((S + Ia − W)/S)², 0)

The internal partition link moves the abstracted part of the rainfall, i·A·(1 − C), from `R1` into `Retention`, where i is the rainfall intensity and A the catchment area. The rest, i·A·C, stays in `R1` and becomes runoff. While W < Ia the bracket is negative, so C = 0 and all rain is abstracted. Once W passes Ia, C rises toward 1 as W approaches 1.2·S. Integrated over a storm, this rate form gives exactly the Curve Number equation for the cumulative runoff depth Q (the technical guide has the derivation):

  Q = (P − Ia)² / (P − Ia + S)  for P > Ia, where P is the cumulative rainfall depth

**Recovery.** The abstraction store drains as dV_W/dt = −k·V_W, with the recovery coefficient k = 0.1 1/day. This lets the method run continuously over several storms. The drained water leaves the model. Over a single 1.5-day event its effect is small.

**Routing (Nash cascade).** Runoff is routed through n equal linear reservoirs, each with outflow Storage/K. The outlet link (`CN_outlet`) carries the discharge of the last reservoir. The residence time K comes from the NRCS lag equation, written for a flow length ℓ in m, slope s in m/m and lag L in days:

  L = ℓ^0.8 · (1000/CN − 9)^0.7 / (176300 · √s),  K = L/(n − 1)

With K = L/(n − 1) the impulse response (a gamma distribution) peaks exactly at the lag for any n. Here:

| Catchment | n | Lag L | K per reservoir |
|---|---|---|---|
| Rural | 5 | 1.26 h | 18.9 min |
| Rural_3res | 3 | 1.26 h | 37.7 min |
| Urban | 5 | 0.48 h | 7.2 min |

With n = 5 the peak of the response is close to the peak of the NRCS dimensionless unit hydrograph. With n = 3 the peak is lower and the recession longer.

**Two composites, one difference.** `CN_Catchment` and `CN_Catchment_3` take the same properties and compute the same runoff volume. They differ only in the number of routing reservoirs, and therefore only in the shape of the hydrograph. Use the 5-reservoir version to reproduce NRCS peak flows. Use the 3-reservoir version where fewer state variables matter more than the peak, for example in large models.

**Chaining.** The `CN_outlet` link from `Rural` enters the surface reservoir `R1` of `Urban`. This inflow is not partitioned (the partition link acts only on rainfall), so the rural runoff is routed through the urban cascade on its way to the outlet. Flows are in m³/day, the model's internal unit (86,400 m³/day = 1 m³/s).

## What to look for in the results

- **Initial abstraction.** The urban runoff fraction leaves zero after 5.6 mm of rain, about 1.2 hours into the storm. The rural one stays at zero until 27.4 mm has fallen, about 2.2 hours in, just before the most intense rain. The rural catchment produces no runoff at all during the first part of the storm.
- **Runoff volumes.** The final volumes are 12,300 m³ for the rural catchment (12.3 mm, 16% of the rain) and 32,000 m³ for the whole watershed, of which 19,700 m³ (49.3 mm, 66% of the rain) comes from the urban area. The Curve Number equation gives 12.31 mm and 49.30 mm. The rural catchment is 2.5 times larger but produces less runoff than the urban one.
- **Peak timing.** The rainfall peaks between 2.50 and 2.75 h. The watershed outlet peaks at 3.4 h (229,000 m³/day, 2.65 m³/s), driven by the fast urban response. Rural runoff peaks at the urban inlet at 4.7 h (126,000 m³/day, 1.46 m³/s). Its lag is longer, and its rainfall excess comes late in the storm because C grows with cumulative rain. The routed rural water gives the watershed hydrograph its raised falling limb.
- **Cascade length.** `Rural_runoff` (n = 5) and `Rural_3res_hydrograph` (n = 3) carry the same volume and peak at about the same time (4.7 h and 4.8 h), but the 3-reservoir peak is 20% lower (1.16 m³/s) and its recession is longer.
- **Recovery.** After the rain stops the runoff fraction falls slowly as the abstraction store empties at 10% per day.

## Assumptions and limitations

- The closure Ia = 0.2·S is fixed. Antecedent moisture is represented only through the initial abstraction depth (zero here, a dry start). There is no AMC I/II/III switching.
- Rainfall is uniform over each catchment.
- The model produces direct runoff only. There is no baseflow, the abstracted water is not tracked as soil moisture, and water removed by recovery leaves the model.
- The lag equation is calibrated for catchments below about 800 ha with CN between 50 and 95. Both catchments are inside that range.
- There is no channel routing between the two sub-watersheds. The rural hydrograph enters the urban cascade directly, so the urban lag also delays the rural runoff.
- The cascade matches the NRCS peak ordinate, not every ordinate of the dimensionless unit hydrograph.
