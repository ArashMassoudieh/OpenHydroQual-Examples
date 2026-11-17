---
title: Horizontal Subsurface-Flow Vegetated Bed
track: storm
level: 2
status: ready
summary: A 150 m² horizontal subsurface-flow vegetated polishing bed treats a continuous 10 m³/day inflow and a short 60 m³/day design surge. Three gravel cells route water below the surface, remove BOD by first-order decay and send excess flow over a capacity-limited bypass.
plugins: [open_channel, svb_subsurface]
features: [Subsurface-flow wetland, Gravel-bed hydraulics, Hydraulic retention time, First-order BOD removal, Capacity-limited bypass]
keywords: [constructed wetland, horizontal subsurface flow, hssf, vegetated bed, gravel bed, treatment wetland, nature based treatment, BOD, first order decay, hydraulic loading rate, hydraulic retention time, Darcy flow, overflow, bypass, stormwater, wastewater]
components:
  BOD: Biochemical oxygen demand represented as a dissolved constituent in g/m³.
  k_BOD: First-order BOD removal coefficient of 0.35 1/day at the fixed 20 °C teaching condition.
  BOD_Removal: First-order reaction that removes dissolved BOD in every water-holding block.
  Inlet_Distribution: "A 6.67 m long, 7.5 m wide distribution channel at the upstream edge of the bed. It receives a continuous 10 m³/day flow and a 0.5-day surge to 60 m³/day, both at 20 g/m³ BOD."
  Aggregate_storage_layer_confined: "Three 6.67 m by 7.5 m gravel cells, each 0.6 m thick with porosity 0.4 and saturated hydraulic conductivity 500 m/day. Together they form a 20 m long, 7.5 m wide subsurface bed."
  Receiving_Water: "A 1 km² receiving-water reservoir initialized at elevation 0.466 m. Its large surface area keeps the downstream stage effectively constant while accepting treated flow and bypass flow."
  Infiltration: Vertical Darcy exchange from the distribution channel into the first gravel cell through a 0.3 m path with interface conductivity 1 m/day.
  Bed_1_to_2: Horizontal Darcy flow from the first to the second gravel cell across a 5 m wide interface.
  Bed_2_to_3: Horizontal Darcy flow from the second to the third gravel cell across a 5 m wide interface.
  Treated_Outflow: Darcy drainage from the last gravel cell to the outlet collector over a 5 m path.
  Surface_Bypass: "A capacity-limited overflow from the distribution channel. Its crest is 0.2 m above the channel floor and its discharge approaches 40 m³/day smoothly."
inputs:
  inflow.csv: "Influent flow in m³/day versus time in day. The base flow is 10 m³/day; a 60 m³/day design surge lasts from day 4.1 to day 4.6, with 0.1-day ramps."
plots:
  - title: Inflow, treated flow and surface bypass
    ylabel: Flow (m³/day)
    series:
      - {column: "Inlet_Distribution_inflow", label: "Influent"}
      - {column: "Treated_Outflow_flow", label: "Treated subsurface flow"}
      - {column: "Surface_Bypass_flow", label: "Surface bypass"}
    caption: The gravel bed carries the base flow; the short design surge raises the inlet and activates the capacity-limited surface bypass.
  - title: Hydraulic head through the gravel bed
    ylabel: Hydraulic head (m)
    series:
      - {column: "Bed_1_head", label: "Bed cell 1"}
      - {column: "Bed_2_head", label: "Bed cell 2"}
      - {column: "Bed_3_head", label: "Bed cell 3"}
    caption: Head declines from the inlet toward the outlet under base flow and rises temporarily during the surge.
  - title: BOD concentration through the bed
    ylabel: BOD (g/m³)
    series:
      - {column: "Inlet_Distribution_BOD:concentration", label: "Influent distribution channel"}
      - {column: "Bed_1_BOD:concentration", label: "Bed cell 1"}
      - {column: "Bed_2_BOD:concentration", label: "Bed cell 2"}
      - {column: "Bed_3_BOD:concentration", label: "Bed cell 3"}
    caption: First-order removal lowers BOD as water moves through the three completely mixed gravel cells.
---

## What this model represents

A horizontal subsurface-flow constructed wetland moves water through a porous gravel bed below the surface. Emergent vegetation grows in the bed, but the water level normally remains below the gravel surface. The porous medium spreads the flow, provides surface area for microbial treatment and gives the water several days of contact time without a permanent open-water surface.

This example represents a small treatment bed receiving a continuous flow of 10 m³/day. The bed is 20 m long, 7.5 m wide and 0.6 m thick, with a 0.4 drainable porosity. Its overall length-to-width ratio is 2.67:1. A short design surge tests its hydraulic capacity. Water that cannot enter the bed raises the inlet distribution channel and can leave through a capped surface bypass.

## How it works

The three `Aggregate_storage_layer_confined` cells each have plan area A = 50 m², thickness b = 0.6 m and porosity n = 0.4. Below the top of the layer, water depth is

  d = S/(A n)

where S is stored water volume. If the layer fills, additional storage raises the head through the confined storativity of 0.05. The hydraulic head in each cell is H = z_b + d, where z_b is its bottom elevation.

Horizontal flow between adjacent cells follows the expression in `aggregate2aggregate_H_Link_b`:

  Q = (H_s - H_e) (K_s + K_e) (b_s + b_e) w / (4 L)

where K is saturated hydraulic conductivity, b is saturated thickness, w is interface width and L is the centre-to-centre distance. With clean gravelly sand K = 500 m/day, w = 7.5 m and L = 6.67 m. The 0.02 m drop in bed elevation per cell supplies a small background slope, while the stored-water gradient adjusts to carry the imposed flow.

Water enters the first cell from the distribution channel through `channel_to_aggregate_link_Kv`:

  Q = (H_s - H_e) K_v A_i / L_v

The interface area A_i is the smaller of the channel water-surface area and the first cell's 50 m² plan area. The interface conductivity K_v is 1 m/day and the vertical path L_v is 0.3 m.

The outlet link uses Darcy flow from the last cell to a large receiving-water reservoir:

  Q = (H_s - H_e) K_s b_s w / L

The surface bypass begins when the inlet head exceeds the 0.8 m crest. Its uncapped rating is Q_w = 15,000(H - 0.8)^1.5 m³/day and its smoothed capacity limit is

  Q = Q_w Q_max / (Q_w^n + Q_max^n)^(1/n)

with Q_max = 40 m³/day and n = 6.

BOD enters at 20 g/m³ and is removed everywhere by the first-order reaction

  dC/dt = -k C

with k = 0.35 1/day. The gravel cells are completely mixed reactors, so longitudinal dispersion within each 10 m cell is implicit.

## What to look for in the results

At the 10 m³/day base flow, the hydraulic loading is 0.0667 m/day. The three bed cells hold 32.2 m³ of pore water, giving a nominal operating residence time of 3.22 days. Their steady heads are 0.549, 0.517 and 0.483 m, and the treated-flow link carries 10.0 m³/day. The downstream reservoir stage changes by only 0.00015 m during the 12-day run, so it acts as an effectively constant receiving-water boundary.

The surge raises the inlet water depth from 0.0093 m to 0.218 m. Its head reaches 0.818 m, 0.018 m above the bypass crest. The bed temporarily carries 25.7 m³/day, while the bypass peaks at 34.2 m³/day and remains above 0.01 m³/day for 0.40 day. Of 150.02 m³ entering over the full run, 139.09 m³ passes through the bed and 10.91 m³ bypasses it. The change in upstream and bed storage is 0.0148 m³, and the integrated water-balance residual is 0.00058 m³, or 0.00039% of inflow.

Before the surge, BOD falls from 20 g/m³ in the imposed inflow to 19.68 g/m³ in the distribution channel, then to 14.21, 10.33 and 7.56 g/m³ through the three cells. This is a 62% concentration reduction across the treatment train at base flow. The short hydraulic pulse raises the final-cell concentration to 10.38 g/m³ at day 5.25, after the flow peak has passed. Across the full simulation, 3,000.4 g of BOD enters, 1,154.1 g leaves in treated flow, 206.9 g leaves in bypass flow and 1,639.4 g is removed by the first-order reaction. The remaining 0.12 g is the increase in stored BOD mass.

## Assumptions and limitations

- The model is a conceptual polishing unit, not a site design. Its 0.6 m media depth, 2.67:1 length-to-width ratio and 500 m/day hydraulic conductivity are within preliminary ranges in the [U.S. EPA subsurface-flow wetland design manual](https://www.epa.gov/system/files/documents/2025-01/subsurface-flow-constructed-wetlands-for-wastewater-treatment-july-1993.pdf), but the values are not calibrated to a particular installation.
- The hydraulic conductivity represents clean coarse gravel. Clogging, root growth and preferential paths can lower the field conductivity and shorten effective residence time.
- Each gravel cell is completely mixed. The three-cell cascade approximates distributed plug flow but does not resolve local velocity variations.
- BOD removal is a single first-order process at a fixed 20 °C. It combines microbial oxidation, filtration and settling into one coefficient and does not track dissolved oxygen, solids accumulation or temperature dependence.
- Vegetation is represented by the treatment-rate assumption. Plant growth, seasonal senescence, evapotranspiration and nutrient uptake are not modelled explicitly.
- The bypass limit represents a downstream pipe capacity. A real design also requires freeboard, erosion protection and a checked emergency overflow.
