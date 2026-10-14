---
title: 2D Soil Cross-Section Under a Furrow
track: soil
level: 2
status: ready
summary: A vertical cross-section of loam soil, 2 m wide and 1.2 m deep, built as a grid of 48 soil cells. Water ponded in an irrigation furrow infiltrates and spreads both downward and sideways as a wetting bulb, then slowly recharges the water table.
plugins: [unsaturated_soil]
features: [2D grid, Lateral flow, Capillary spreading, Furrow infiltration, Water table]
keywords: [2d, two dimensional, grid, mesh, grid generator, cross section, lateral flow, capillarity, wetting bulb, furrow irrigation, infiltration trench, unsaturated flow, richards equation, van genuchten, symmetry boundary, recharge, water table, anisotropy]
components:
  Furrow: "Half of a 0.5 m wide irrigation furrow, seen in cross-section (the model uses the symmetry plane through the furrow centre as its left edge). It starts with 0.1 m of water over its 0.25 m² footprint per metre of furrow length (25 L), which is the only water added. It is a Catchment block with no outlet; the Manning coefficient is required by the block type but unused."
  Soil: "48 loam cells in 8 columns and 6 rows, named Soil_column_row (Soil_1_1 is under the furrow at the surface, Soil_8_6 is at the far bottom corner). Each is 0.25 m wide, 0.2 m tall and 1 m deep into the page. Loam van Genuchten parameters from Carsel and Parrish (1988). The initial moisture is in hydrostatic equilibrium with the water table, from θ = 0.228 in the top row to θ = 0.375 in the bottom row."
  Water_table: A fixed water table at −1.2 m elevation, the base of the domain.
  Furrow_infiltration: Moves ponded water from the furrow into Soil_1_1. Positive downward.
  soil_to_soil_H_link: "35 horizontal links between neighbouring cells in the same row (named H_12_1 for columns 1 to 2 in row 1, and so on). Face area 0.2 m² (cell height × 1 m), length 0.25 m. Positive from the lower-numbered to the higher-numbered column, i.e. away from the furrow."
  soil_to_soil_link: "40 vertical links between neighbouring cells in the same column (named V_1_12 for rows 1 to 2 in column 1, and so on). Positive downward."
  soil_to_fixedhead_link: "Eight links (WT_1 to WT_8) from the bottom row to the water table. Positive downward (recharge)."
plots:
  - title: Water in the furrow
    ylabel: Ponded depth (m)
    series:
      - {column: "Furrow_depth", label: "Furrow"}
    caption: The furrow drains in about 6 hours. Infiltration is fastest at the start, when the soil below is driest.
  - title: Lateral spreading in the top row
    ylabel: θ (m³/m³)
    series:
      - {column: "Soil_1_1_theta", label: "0 to 0.25 m from furrow centre"}
      - {column: "Soil_2_1_theta", label: "0.25 to 0.5 m"}
      - {column: "Soil_3_1_theta", label: "0.5 to 0.75 m"}
      - {column: "Soil_4_1_theta", label: "0.75 to 1.0 m"}
      - {column: "Soil_6_1_theta", label: "1.25 to 1.5 m"}
    caption: Water spreads sideways from the furrow by capillarity alone. The front arrives later and weaker in each successive column, and the soil beyond 1 m is barely touched.
  - title: Downward movement under the furrow
    ylabel: θ (m³/m³)
    series:
      - {column: "Soil_1_1_theta", label: "0 to 0.2 m depth"}
      - {column: "Soil_1_2_theta", label: "0.2 to 0.4 m"}
      - {column: "Soil_1_3_theta", label: "0.4 to 0.6 m"}
      - {column: "Soil_1_4_theta", label: "0.6 to 0.8 m"}
      - {column: "Soil_1_6_theta", label: "1.0 to 1.2 m"}
    caption: Under the furrow the wetting front moves down and dampens with depth. The shallow cells drain back as the water moves deeper and outward.
  - title: Recharge to the water table
    ylabel: Flow (m³/day)
    series:
      - {column: "WT_1_flow", label: "Below the furrow (column 1)"}
      - {column: "WT_2_flow", label: "Column 2"}
      - {column: "WT_3_flow", label: "Column 3"}
      - {column: "WT_4_flow", label: "Column 4"}
    caption: Recharge starts about a day after irrigation and is spread over a wider strip than the furrow, because the water has moved sideways on its way down.
---

## What this model represents

When water infiltrates from a narrow source, such as an irrigation furrow, a drip line, an infiltration trench or a leaking pipe, it does not move straight down. Capillary suction in the drier soil around the source pulls water sideways while gravity pulls it down, and the wetted zone takes the shape of a bulb. How wide the bulb gets decides, for example, how far apart furrows or drip lines can be, and how much of the applied water ends up below the root zone.

A one-dimensional column cannot show this. This model is a vertical cross-section through the soil perpendicular to a furrow, 2 m wide and 1.2 m deep, discretized into a grid of 8 × 6 soil cells that are connected both vertically and horizontally. Because a furrow is symmetric about its centreline, only half of it is modelled: the left edge of the grid is the furrow centreline and carries no flow. All results are per metre of furrow length.

Grids like this one can be generated in the OpenHydroQual interface with the grid generator, which creates the cells and the horizontal and vertical links in one step.

## How it works

The expressions below are from `unsaturated_soil.json`, the current soil plugin.

**Soil cells.** Every cell is a `Soil` block with the same loam properties (θₛ = 0.43, θᵣ = 0.078, α = 3.6 1/m, n = 1.56, K_sat = 0.25 m/day). Moisture content, effective saturation and pressure head follow the van Genuchten relationships:

  θ = S/(A·d),  Sₑ = (θ − θᵣ)/(θₛ − θᵣ) limited to 0.001 to 0.999
  ψ = −(1/α)·(Sₑ^(−1/m) − 1)^(1/n),  m = 1 − 1/n

and the total head is H = z_bottom + d + ψ (pressure head referred to the top of the cell). In this model A is the cell's plan area (0.25 m × 1 m) and d its height (0.2 m). The *1D Infiltration and Soil Boundary Conditions* example gives the full set of soil equations, including the treatment of saturation.

**Vertical links** (`soil_to_soil_link`) compute their length and area from the two cells:

  Q = K_eff · (H_upper − H_lower)/L · A,  L = (d₁ + d₂)/2

**Horizontal links** (`soil_to_soil_H_link`) take the face area and the distance between cell centres as properties (0.2 m² and 0.25 m):

  Q = K_eff · (H₁ − H₂)/L · A_face

Both cells in a row have the same elevation, so a horizontal flow is driven only by the difference in pressure head: water moves sideways by capillarity. In both link types

  K_eff = K_sat · [1 − (1 − Sₑ^(1/m))^m]²

using the larger of the two cells' Sₑ and the mean of their m. For the horizontal link K_sat is the mean of the two cells' K_sat multiplied by their `aniso_ratio`. The anisotropy ratio is 1 here (isotropic soil); setting it above 1 makes horizontal flow easier, as in a layered soil.

**Furrow.** The furrow is a `Catchment` block over the first column, connected to Soil_1_1 by a `surfacewater_to_soil_link`:

  Q = K_sat · (H_furrow − H_cell)/(d/2) · A · h_p/(h_p + 0.001 m)

where H_furrow = 0 m + h_p and h_p is the ponded depth. It starts with h_p = 0.1 m.

**Boundaries.** The left edge (the furrow centreline) and the right edge (2 m away) have no links, so no water crosses them. The soil surface outside the furrow is closed: there is no rain and no evaporation. Each bottom cell exchanges water with the water table at −1.2 m through Q = K_eff·(H − H_wt)/(d/2)·A.

**Initial condition.** All cells start in hydrostatic equilibrium with the water table (H = −1.2 m everywhere, given the top-of-cell head reference), so nothing moves until the furrow is filled.

## What to look for in the results

- **Furrow infiltration.** The 25 L in the half-furrow infiltrates in about 6 hours (the furrow is empty at day 0.26). The initial rate is 0.68 m³/day per metre of furrow, falling as the soil under the furrow wets up.
- **Shape of the wetting bulb.** Six hours after irrigation, the cell under the furrow is nearly saturated (θ = 0.41), the wetting has reached about 0.6 m deep and 0.5 m sideways, and the soil 0.75 m from the centreline has not yet changed. After one day the top row reads θ = 0.327, 0.303, 0.258, 0.230 in columns 1 to 4. The bulb is about as wide as it is deep: in this fine-textured soil with a moderately dry start, capillary spreading is comparable to gravity drainage over the first day.
- **Redistribution.** After the furrow empties, the cells nearest the source drain and the water spreads further out and down. By day 5 the top row has evened out (θ = 0.271 under the furrow down to 0.238 at 0.75 to 1.0 m), and cells beyond 1.25 m from the centre are still at their initial moisture.
- **Delayed and widened recharge.** Almost nothing reaches the water table during the first day. Recharge under the furrow peaks after about 3 days, and by day 5 it is spread across the first five columns (1.25 m), five times the width of the half-furrow. By day 5, 5.5 L of the 25 L applied (22%) has reached the water table and the rest is still held in the soil.
- **Water balance.** Water applied (24.7 L in the half-furrow) = change in soil storage (19.1 L) + recharge (5.5 L).

## Assumptions and limitations

- The cross-section is two dimensional: flow along the furrow is ignored, and the furrow is assumed long and uniform.
- The grid is coarse (0.25 m × 0.2 m). The wetting front is smeared over one or two cells, and finer cells near the furrow would sharpen it at the cost of run time.
- The soil is homogeneous and isotropic, with no root uptake, no evaporation and no rain.
- The furrow is filled once and instantly, and its wetted perimeter is represented only by its flat bottom over the first column. Infiltration through the furrow side walls is not represented.
- Because the soil plugin refers each cell's head to its top, the link to the water table and the furrow link use a distance of half a cell thickness from that reference. The internal links are unaffected because all cells have the same size.
