---
title: 1D Infiltration and Soil Boundary Conditions
track: soil
level: 1
status: ready
summary: Two identical layered soil columns receive the same intense 100 mm application. Richards' equation with van Genuchten properties shows ponding, a perched wetting front at the layer contact, and how a free-drainage bottom and a water-table bottom change what happens next.
plugins: [unsaturated_soil]
features: [Richards equation, Van Genuchten soil, Ponding, Free drainage, Water table boundary]
keywords: [infiltration, richards equation, van genuchten, mualem, unsaturated flow, vadose zone, soil moisture, wetting front, ponding, layered soil, perched water, hydraulic conductivity, free drainage, unit gradient, water table, lower boundary condition, redistribution, soil column, lysimeter]
components:
  Storm: "A short, intense water application: 100 mm in 2 hours (50 mm/h) starting at day 0.5, read from `storm.txt`. Both columns receive it. The rate is chosen to exceed the infiltration capacity of the soil so that water ponds at the surface."
  Surface_A: The 1 m² ground surface above column A. It is a Catchment block with no outlet, so rain that cannot infiltrate collects on it as ponded water. Its surface elevation is 0 m. The Manning coefficient is required by the block but unused, because no runoff link is attached.
  Surface_B: The same surface over column B.
  Soil: "Twenty 0.1 m soil cells, ten per column (Soil_A01 to Soil_A10 and Soil_B01 to Soil_B10, numbered from the top). Cells 01 to 04 (0 to 0.4 m depth) are a sandy loam and cells 05 to 10 (0.4 to 1.0 m) are a loam, using the Carsel and Parrish (1988) class-average van Genuchten parameters. Both columns start from the same moisture profile, in hydrostatic equilibrium with a water table at −1.0 m."
  Drainage_outlet: A sink below column A. Because the link into it imposes a fixed hydraulic gradient, its head (−2 m) does not affect the flow.
  Water_table: A fixed water table at −1.0 m elevation, the base of column B.
  Infiltration_A: Moves ponded water from Surface_A into the top soil cell. Positive downward.
  Infiltration_B: The same for column B.
  soil_to_soil_link: Vertical Darcy-Buckingham flow between neighbouring cells of the same column (nine links per column, named Flow_A01_A02 and so on). Positive downward, negative when water moves up by capillary rise.
  Free_drainage: "Unit-gradient (free drainage) lower boundary of column A: outflow equals the unsaturated hydraulic conductivity of the bottom cell. Water can only leave."
  Water_table_exchange: "Lower boundary of column B: Darcy flow between the bottom cell and the water table. Positive downward (recharge); negative values would mean capillary supply from the water table."
inputs:
  storm.txt: "Rainfall in the OpenHydroQual precipitation format: start time (day), end time (day), depth (m) per row. Twelve 10-minute intervals of 8.33 mm between day 0.5 and day 0.5833, padded with dry intervals that cover the whole simulation."
plots:
  - title: Infiltration during the storm
    ylabel: Rate (m/day)
    series:
      - {column: "Surface_A_Precipitation", label: "Rainfall rate"}
      - {column: "Infiltration_A_flow", label: "Infiltration rate, column A"}
      - {column: "Infiltration_B_flow", label: "Infiltration rate, column B"}
    caption: Rain arrives at 1.2 m/day. Infiltration first nearly matches it, then falls to about 0.83 m/day as the top layer fills, and the excess ponds. The two columns behave identically at the surface, so their infiltration lines overlap.
  - title: Ponded water depth
    ylabel: Depth (m)
    series:
      - {column: "Surface_A_depth", label: "Column A"}
      - {column: "Surface_B_depth", label: "Column B"}
    caption: Water stands on the surface for about 3 hours and peaks at 18 mm when the storm stops.
  - title: Moisture content, column A (free drainage)
    ylabel: θ (m³/m³)
    series:
      - {column: "Soil_A01_theta", label: "0.0 to 0.1 m"}
      - {column: "Soil_A04_theta", label: "0.3 to 0.4 m (above contact)"}
      - {column: "Soil_A05_theta", label: "0.4 to 0.5 m (below contact)"}
      - {column: "Soil_A08_theta", label: "0.7 to 0.8 m"}
      - {column: "Soil_A10_theta", label: "0.9 to 1.0 m"}
    caption: The wetting front passes each depth in turn. The bottom cell drains before the storm and after it, because nothing holds water up at the base.
  - title: Moisture content, column B (water table)
    ylabel: θ (m³/m³)
    series:
      - {column: "Soil_B01_theta", label: "0.0 to 0.1 m"}
      - {column: "Soil_B04_theta", label: "0.3 to 0.4 m (above contact)"}
      - {column: "Soil_B05_theta", label: "0.4 to 0.5 m (below contact)"}
      - {column: "Soil_B08_theta", label: "0.7 to 0.8 m"}
      - {column: "Soil_B10_theta", label: "0.9 to 1.0 m"}
    caption: Nothing moves until the storm, because the profile starts at equilibrium. Afterwards the deep cells return towards their equilibrium moisture and the bottom cell stays close to saturation.
  - title: Flux out of the bottom
    ylabel: Flux (m/day)
    series:
      - {column: "Free_drainage_flow", label: "Column A, free drainage"}
      - {column: "Water_table_exchange_flow", label: "Column B, water table"}
    caption: Column A drains from the first moment. Column B releases nothing until the wetting front reaches the water table, then returns the storm water over the next few days.
---

## What this model represents

A soil column is the simplest setting in which to see variably saturated flow. Water applied at the top first fills the pores near the surface, then moves downward as a wetting front, and finally redistributes or drains, depending on what sits below the column. The upper boundary decides how much water gets in. The lower boundary decides where it goes.

This model places two identical 1.0 m columns side by side and gives both the same intense water application (100 mm in 2 hours). They differ only in their lower boundary:

- **Column A** ends in **free drainage** (a unit hydraulic gradient), the usual assumption for a deep vadose zone or a lysimeter that drains freely.
- **Column B** sits on a **water table** at its base, the situation in a shallow groundwater area.

Each column is layered: 0.4 m of sandy loam over 0.6 m of loam. A coarser soil over a finer one is common in alluvial and constructed soils, and it creates a perched, nearly saturated zone at the contact while the wetting front passes. The same setup can be used to examine stormwater infiltration practices, irrigation, or the sensitivity of recharge to the depth of the water table.

## How it works

**Soil cells.** Each column is a stack of ten `Soil` blocks, 0.1 m thick with a 1 m² plan area. Each cell stores water and computes its state from that storage. The expressions below are from `unsaturated_soil.json`, the current soil plugin (the older variants in the resources folder are not used). With storage S, area A and thickness d:

  θ = S / (A·d)
  Sₑ = (θ − θᵣ) / (θₛ − θᵣ), limited to the range 0.001 to 0.999
  ψ_suction = −(1/α)·(Sₑ^(−1/m) − 1)^(1/n), with m = 1 − 1/n (van Genuchten)

When θ is pushed above the 0.999 saturation limit, the cell becomes pressurized through the specific storage Sₛ (0.01 1/m here):

  ψ_excess = θₛ · max((θ − θᵣ)/(θₛ − θᵣ) − 0.999, 0) / Sₛ
  ψ = ψ_suction + ψ_excess

and the total head is

  H = z_bottom + d + ψ

The plugin refers ψ to the **top** of the cell (z_bottom + d), not its midpoint. Because every cell uses the same convention, gradients between cells are unaffected, but the initial condition has to respect it (see below).

| Layer | Cells | Depth (m) | θₛ | θᵣ | α (1/m) | n | K_sat (m/day) |
|---|---|---|---|---|---|---|---|
| Sandy loam | 01 to 04 | 0.0 to 0.4 | 0.41 | 0.065 | 7.5 | 1.89 | 1.061 |
| Loam | 05 to 10 | 0.4 to 1.0 | 0.43 | 0.078 | 3.6 | 1.56 | 0.250 |

**Flow between cells** (`soil_to_soil_link`) is Darcy-Buckingham flow:

  Q = K_eff · (H_upper − H_lower) / L · A
  K_eff = K_sat · [1 − (1 − Sₑ^(1/m))^m]²

with L the mean of the two thicknesses, K_sat the **smaller** of the two cells' saturated conductivities, m the mean of the two cells' m, and Sₑ the **larger** of the two effective saturations (capped at 0.999), so the wetter cell controls the relative conductivity. This is the Mualem-van Genuchten relative conductivity without the Sₑ^0.5 pore-connectivity factor. Positive Q is downward.

**Surface ponding.** Each surface is a `Catchment` block with no outlet. Rain from `Storm` is added to its storage, and its ponded depth is h_p = S/A. The `surfacewater_to_soil_link` moves ponded water into the top cell:

  Q_inf = K_sat,top · (H_surface − H_top) / (d_top/2) · A · h_p/(h_p + 0.001 m)

where H_surface = elevation + h_p. The last factor switches infiltration off smoothly when less than about 1 mm of water is present, so the ponded depth cannot go negative. Rain is first added to the surface and infiltrates from there: the ponded depth stays near zero while the soil can accept the rain, and grows when it cannot.

**Lower boundaries.**

- *Free drainage* (`fixed_hydraulic_gradient_link`, gradient i = 1): Q = i · K_eff · A, where K_eff uses the bottom cell's Sₑ. Outflow is simply the unsaturated conductivity of the bottom cell.
- *Water table* (`soil_to_fixedhead_link`): Q = (H_bottom − H_wt) · K_eff / (d/2) · A, again with K_eff from the bottom cell. The flux can reverse, which would represent capillary rise from the water table.

**Initial condition.** Every cell starts at the moisture content that puts it in hydrostatic equilibrium with a water table at −1.0 m: ψ = −1.0 m − (z_bottom + d), so H = −1.0 m everywhere. Moisture therefore increases with depth, from θ = 0.122 in the top cell to θ = 0.407 in the bottom cell. Column B is exactly at rest until the storm. Column A starts from the same profile but begins draining at once, because its lower boundary does not hold water up.

**Rainfall input.** OpenHydroQual converts each row of a precipitation file into a rate (depth divided by duration) at the interval midpoint and interpolates linearly between midpoints. The storm is therefore written as short intervals with dry rows before and after it, and the dry rows extend to the end of the simulation so that the rate is exactly zero outside the storm.

## What to look for in the results

- **Time to ponding.** For the first few minutes the dry sandy loam takes almost all the rain: infiltration peaks at about 1.17 m/day against a rain rate of 1.2 m/day, then declines as the top cells approach saturation. Ponding begins about 4 minutes into the storm, and water stands on the surface for about 3 hours (day 0.503 to 0.623). The deepest ponding, 18 mm, occurs when the rain stops.
- **Infiltration capacity.** During ponding, infiltration settles near 0.83 m/day. This is below the sandy loam's K_sat (1.06 m/day) because the loam below, with a K_sat of 0.25 m/day, cannot carry water away as fast as the upper layer receives it.
- **Perching at the layer contact.** The wetting front reaches the contact at 0.4 m by the end of the storm. Cells 04 and 05 peak at θ = 0.39 and 0.41 (close to saturation) between days 0.73 and 0.82, while the soil at 0.7 m is still at its initial moisture. Water piles up above the slower loam before it can move on.
- **The lower boundary decides the fate of the water.** The two columns are identical at the surface and in the upper layer, and differ only in the deeper loam.
  - *Column A* (free drainage) loses 10 mm before the storm even starts and 120 mm in all over 10 days, more than the 100 mm applied. It ends drier than it started (0.236 m of stored water against 0.257 m). Its outflow peaks at 0.036 m/day around day 1.5.
  - *Column B* (water table) releases nothing until the wetting front arrives at about day 0.75. Because its bottom cell stays nearly saturated (θ never below 0.407), the boundary conducts well and the outflow peaks earlier and higher, at 0.050 m/day near day 1.2. Over the 10 days it passes 91 mm to the water table and ends with 9 mm more water than it started with, still draining slowly towards equilibrium.
- **Water balance.** For each column, storage change = applied rain − bottom outflow, to the precision of the output sampling. For column B: 0.2565 m + 0.100 m − 0.0909 m = 0.2656 m, the final storage.

## Assumptions and limitations

- Flow is strictly vertical and one dimensional. There is no lateral flow, no evaporation from the surface and no root uptake (see the plant examples for transpiration).
- Each cell is 0.1 m thick, which smears the wetting front over two or three cells. Thinner cells sharpen it at the cost of run time.
- The relative conductivity omits the Mualem Sₑ^0.5 factor, and the conductivity between cells uses the wetter cell's saturation and the smaller K_sat. This upstream-like weighting is robust, but it differs from the arithmetic or geometric means used in some other codes.
- Air entrapment, hysteresis and macropore flow are not represented.
- The ponded surface has no outlet. In a real field the excess would run off once it exceeds depression storage.
- The storm (100 mm in 2 hours) is deliberately extreme so that ponding is clear. It is closer to a flood-irrigation event than to most natural rainfall.
