---
title: Soil Column Breakthrough
track: wq
level: 2
status: ready
summary: A 1 m saturated soil column fed with a 30-day pulse of copper and a bromide tracer. Bromide shows advection and dispersion alone; copper is retarded fivefold by kinetic sorption, arrives late, and tails long after the pulse ends.
plugins: [groundwater, mass_transfer]
features: [1D transport, Kinetic sorption, Retardation, Breakthrough curve, Analytical check]
keywords: [column, soil column, breakthrough, btc, porous media, transport, advection dispersion, ade, dispersivity, retardation, retardation factor, kinetic sorption, nonequilibrium, tailing, tracer, bromide, copper, kd, ogata banks, numerical dispersion, lab experiment, lysimeter]
extra_files: [analytical_bromide.csv, analytical_cu_equilibrium.csv]
components:
  Groundwater cell: "Twenty saturated soil cells, Cell_01 at the top (inlet) to Cell_20 at the bottom (outlet). Each is 1 m² in cross section and 0.05 m long, with porosity and moisture content 0.4, so it holds 0.02 m³ of water. The diagram draws them as four stacks of five, read top to bottom and left to right. Cell_01 receives the inflow from `flow.txt` with the concentrations in `inflow_concentration.txt`."
  Outlet: "A fixed-head boundary below the column that receives the effluent. Its state is not solved for, so it acts as a free outflow."
  Time-Dependent flow: "Twenty links that carry the water downward at 0.1 m³/day (`flow.txt`). Flow_01 to Flow_19 join neighbouring cells, are 0.05 m long and have 1 m² of area, which sets the dispersive exchange between cells. Flow_20 joins Cell_20 to the Outlet boundary. Its length is set to 1000 m so that the dispersive term α·Q/L, which would otherwise draw solute into the zero-concentration boundary, is negligible and the outflow is purely advective. Positive flow is downward."
  Bromide: "A conservative tracer. It moves with the water and is not sorbed or degraded."
  Cu_aq: "Dissolved copper (g/m³ of pore water). Moves with the water and exchanges with the solid."
  Cu_s: "Copper sorbed on the soil. An Immobile_Constituent: it does not move between cells. Its concentration is mass per volume of pore water (g/m³); the loading per mass of soil is q = θ·Cu_s/ρ_b (g/kg)."
  K_d: "Linear distribution coefficient (m³/kg). 0.001 m³/kg is 1 L/kg."
  k_s: "First-order sorption rate coefficient (1/day)."
  rho_b: "Dry bulk density of the soil (kg/m³)."
  theta: "Porosity of the saturated soil (dimensionless), used to convert between pore-water and solid-phase concentrations."
  Sorption: "Net transfer of copper from the pore water to the soil, rate k_s·(Cu_aq − θ·Cu_s/(ρ_b·K_d)). Negative values mean desorption."
inputs:
  flow.txt: "Flow rate through the column (m³/day) versus time (days): a constant 0.1 m³/day. Read both as the inflow of Cell_01 and as the flow of every link."
  inflow_concentration.txt: "Concentration of the inflow (g/m³) versus time (days), used for both bromide and copper: 8 g/m³ from day 0 to day 30, then 0."
  analytical_bromide.csv: "Ogata-Banks solution for the bromide pulse at the column outlet (days, g/m³), with dispersivity 0.05 m. For the comparison plot only."
  analytical_cu_equilibrium.csv: "Ogata-Banks solution for copper assuming instantaneous (equilibrium) sorption, R = 5 (days, g/m³). For the comparison plot only."
plots:
  - title: Breakthrough curves at the outlet
    ylabel: Concentration (g/m³)
    series:
      - {column: "Cell_20_Bromide:concentration", label: "Bromide (model)"}
      - {column: "Cell_20_Cu_aq:concentration", label: "Copper (model, kinetic sorption)"}
      - {file: "analytical_bromide.csv", label: "Bromide, analytical", style: points}
      - {file: "analytical_cu_equilibrium.csv", label: "Copper, equilibrium sorption (analytical)", style: dashed}
    caption: Bromide breaks through after one pore volume (4 days). Copper arrives five times later; kinetic sorption makes it break through earlier and more gradually than the equilibrium solution and leaves a long tail after the pulse.
  - title: Copper held by the soil
    ylabel: Sorbed Cu (g/m³ of pore water)
    series:
      - {column: "Cell_05_Cu_s:concentration", label: "0.20 to 0.25 m depth"}
      - {column: "Cell_10_Cu_s:concentration", label: "0.45 to 0.50 m depth"}
      - {column: "Cell_20_Cu_s:concentration", label: "0.95 to 1.00 m depth"}
    caption: The sorbed front moves down the column during loading and the soil is stripped from the top down once clean water arrives at day 30.
---

## What this model represents

A column experiment: soil is packed in a tube, water is pumped through it at a steady rate, and a solution containing a contaminant is fed for a while before switching back to clean water. Measuring the effluent gives a **breakthrough curve**. The usual practice is to add a conservative tracer (here bromide) to the same feed. The tracer fixes the water velocity and dispersivity, and the difference between the tracer and the contaminant curves isolates sorption.

Here the column is 1 m long and 1 m² in cross section, which can be read as a large laboratory column, a lysimeter or a 1 m soil profile below an infiltration practice. Water moves through it at a Darcy flux of 0.1 m/day. The feed carries 8 g/m³ of both bromide and copper for 30 days, then clean water for another 50 days.

## How it works

**Water.** The column is divided into 20 Groundwater cells of length Δx = 0.05 m. Each holds V = A·Δx·θ = 1 × 0.05 × 0.4 = 0.02 m³ of water. The flows are prescribed: 0.1 m³/day enters Cell_01 and the same flow passes through every link. The water storage therefore stays constant, and the average pore-water velocity is

  v = Q/(A·θ) = 0.1/(1 × 0.4) = 0.25 m/day

One pore volume (0.4 m³) passes in θ·L·A/Q = 4 days.

**Transport.** For each mobile constituent, a link carries an advective flux taken from the upstream cell plus a dispersive flux proportional to the concentration difference (from the `Constituent` definition):

  J = Q·C_upstream + (α·Q/Δx)·(C_from − C_to)

where α is the constituent's dispersivity and Δx is the link length. Bromide and Cu_aq use α = 0.025 m. Because each cell is fully mixed, the upstream scheme adds numerical dispersion of about Δx/2 = 0.025 m, and the implicit time stepping adds about v·Δt/2 ≈ 0.0025 m (the time step is capped at 0.02 day). The column therefore behaves as if the dispersivity were about 0.05 m, which is what the input value was chosen to produce. The Péclet number is L/α ≈ 20.

**Sorption.** The sorbed copper Cu_s is an `Immobile_Constituent`, which has no link transport. Its concentration is computed as mass divided by the water volume in the cell. The single reaction moves copper between the two phases:

  r = k_s · (Cu_aq − θ·Cu_s/(ρ_b·K_d))

with stoichiometric coefficients −1 for Cu_aq and +1 for Cu_s. OpenHydroQual multiplies the rate by each cell's water volume, so the mass gained by the soil equals the mass lost from the water. At equilibrium the sorbed loading per mass of soil is q = θ·Cu_s/ρ_b = K_d·Cu_aq, a linear isotherm. Under equilibrium the copper front would move slower than the water by the retardation factor

  R = 1 + ρ_b·K_d/θ = 1 + 1600 × 0.001/0.4 = 5

so copper would need 5 pore volumes, or 20 days, to reach the outlet. With k_s = 2 per day the sorbed phase relaxes toward equilibrium at a rate k_s·θ/(ρ_b·K_d) = 0.5 per day, about a 2-day time scale. This is short compared with the 20-day travel time, but not instantaneous.

**Analytical check.** The Ogata-Banks solution of the one-dimensional advection-dispersion equation with a step input, superimposed to form the 30-day pulse, gives the bromide curve at the outlet (R = 1) and the equilibrium copper curve (R = 5). Both use α = 0.05 m.

## What to look for in the results

- **Tracer.** Bromide reaches half the feed concentration at the outlet at 3.8 days, about one pore volume, and matches the analytical solution to within about 0.1 g/m³. It drops back to near zero within 6 days after the feed stops.
- **Retardation.** Copper reaches half the feed concentration at 18.5 days, close to R = 5 pore volumes. Its curve is much more spread out than the bromide curve, because the same dispersion acts over a five times longer travel time and because sorption is kinetic.
- **Nonequilibrium.** Compared with the equilibrium solution (dashed), the kinetic copper curve starts earlier (1.2 g/m³ at day 10 against 0.1 g/m³), never reaches the feed concentration (peak 7.1 g/m³ at day 34), and tails far longer (1.2 g/m³ at day 60 against 0.6 g/m³). Early breakthrough with long tailing is the classic signature of rate-limited sorption in column data.
- **Desorption front.** After day 30 clean water strips copper from the top of the column first. The sorbed concentration at 0.25 m depth falls while the deepest cell is still near its peak (28 g/m³ at day 36). The peak value of about 32 g/m³ of pore water corresponds to q = 0.4 × 32/1600 = 0.008 g/kg (8 mg/kg), which is K_d × 8 g/m³.
- **Mass recovery.** The feed delivers 0.1 m³/day × 8 g/m³ × 30 days = 24 g of each constituent. Integrating the mass transfer through Flow_20 gives 24.00 g of bromide and 23.95 g of copper leaving the column by day 80, and 0.05 g of copper is still sorbed in the column. The dispersive part of the outlet flux is 0.0006 g.

## Assumptions and limitations

- The column is saturated and the flow is steady and prescribed; heads and hydraulic conductivity play no role.
- Sorption is linear, reversible and first order, with a single sorption site. Two-site models (an equilibrium fraction plus a kinetic fraction) or nonlinear isotherms are common refinements.
- The 20-cell grid adds numerical dispersion of about Δx/2. The physical dispersivity was reduced by this amount so that the total matches the target value of 0.05 m; when refining the grid, increase the input dispersivity accordingly.
- Bromide and copper use the same dispersivity; molecular diffusion is neglected.
- The effluent concentration is read from Cell_20, the well-mixed bottom cell.
