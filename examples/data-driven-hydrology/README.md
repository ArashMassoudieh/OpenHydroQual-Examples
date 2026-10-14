---
title: Physics-Informed Data-Driven Hydrology
track: hydro
level: 3
status: ready
summary: A rainfall-to-streamflow model for a 1 km² catchment built from generic storage units connected by links that move water down the difference of a latent "potential". Driven by one year of measured daily rainfall (BWI airport, 2010). The structure conserves mass exactly; the shapes and parameters are meant to be learned from data.
plugins: [physicsbaseddatadrivenhydrology]
features: [Storage units, Latent-variable links, Power-law storage, Mass-conserving model structure, Calibration-ready parameters]
keywords: [data driven, machine learning, physics informed, physics guided, hybrid model, grey box, latent variable, potential, power law, nonlinear reservoir, storage unit, conceptual model, rainfall runoff, streamflow, baseflow, quickflow, network model, mass conservation, calibration, parameter estimation]
components:
  Soil_store: 'Fast store (`Storage Unit`) with a capacity of 30,000 m³ (30 mm over 1 km²), starting 30% full. Receives the effective rainfall. Its latent variable rises steeply as it fills, so it sheds water quickly in wet periods.'
  Groundwater_store: 'Slow store (`Storage Unit (Power-law)`) starting at 50,000 m³. Its latent variable is 2×10⁻¹¹·S², a quadratic function of storage, so it drains as a nonlinear reservoir.'
  Stream: Outlet (`Fixed Latent Variable Unit`) with its latent variable fixed at 0. Its storage starts at zero and accumulates all streamflow.
  Direct_runoff: 'Link from the fast store to the stream, transmissivity 3000. Carries the quick response to rain.'
  Percolation: 'Link from the fast store to the slow store, transmissivity 4500. Normally downward; it reverses when the slow store has the higher latent variable.'
  Baseflow: 'Link from the slow store to the stream, transmissivity 10,000. Carries the slow, sustained flow.'
inputs:
  rainfall.csv: 'Daily rainfall (m/day) versus time (days from 1 January 2010) for 2010, aggregated from NOAA hourly precipitation at Baltimore/Washington International Airport (BWI), Maryland (US public domain). Each day is written as a step (two points, at the start and just before the end of the day). Two columns, no header. Total 863 mm.'
plots:
  - title: Rainfall
    ylabel: Rainfall (m/day)
    series:
      - {column: "Soil_store_Precipitation", label: "Daily rainfall, BWI 2010"}
    caption: The measured forcing. The largest day (118 mm) is 30 September, near day 272.
  - title: Streamflow and its two paths
    ylabel: Flow (m³/day)
    series:
      - {column: "Direct_runoff_flow", label: "Direct runoff (fast store)"}
      - {column: "Baseflow_flow", label: "Baseflow (slow store)"}
    caption: Direct runoff makes the storm peaks; baseflow is a smooth, delayed signal. Over the year each carries about half of the water.
  - title: Latent variables
    ylabel: Latent variable (–)
    series:
      - {column: "Soil_store_Latent_variable", label: "Fast store"}
      - {column: "Groundwater_store_Latent_variable", label: "Slow store"}
    caption: The water moves down these potentials. The fast store's potential spikes in storms; when it drops below the slow store's potential, percolation reverses.
  - title: Store contents
    ylabel: Storage (m³)
    series:
      - {column: "Soil_store_Storage", label: "Fast store"}
      - {column: "Groundwater_store_Storage", label: "Slow store"}
    caption: The fast store fills and empties within days; the slow store integrates the whole season.
---

## What this model represents

Data-driven streamflow models (neural networks and other regressions) can fit hydrographs well but are free to create or destroy water. Conceptual models conserve water but fix the shape of every storage–discharge relation in advance. The `physicsbaseddatadrivenhydrology` plugin sits between the two. It provides generic storage units, each with a **latent variable** (a generalized potential computed from its storage), and one kind of link that moves water from higher to lower potential. Any network of these units conserves mass exactly, and the shapes of the potentials and the link conductances are parameters to be learned from rainfall and streamflow records. This is the sense in which the approach is "physics-informed": mass balance and down-gradient flow are imposed, and the rest is fitted.

This example builds the smallest useful network for a 1 km² catchment: a fast store and a slow store that both drain to an outlet. It is driven by one year of measured daily rainfall (2010, Baltimore/Washington International Airport, Maryland). Its parameters were set by hand to give a plausible humid-region hydrograph. There is no observed streamflow in this example, so the model is not trained; it shows what the building blocks compute and how the network behaves, as a starting point for calibration.

## How it works

**Links.** Every link computes

  Q = T · (φ_from − φ_to)

where T is the link's `Mean_Transmissivity` and φ the latent variables of the two ends. Flow is positive from `from` to `to` and reverses when the potential difference does. Here φ is dimensionless and T has units of m³/day per unit potential. (The plugin labels T as m²/day, which matches only if φ is a length such as a head.)

**Fast store (`Storage Unit`).** With storage S, capacity C and fill ratio r = S/C, its latent variable is

  φ = s · r/(1 − r) − 0.0001/r

with scale factor s = 1. The first term rises without bound as the store approaches its capacity, so outflow grows as fast as needed and the store never overfills: a smooth form of saturation-excess behavior. The second term goes to −∞ as the store empties, so links reverse and refill it before it can go dry. Rainfall enters directly:

  dS/dt = c_P · P(t) − Σ Q_out

where P is the rainfall rate in `rainfall.csv` (m/day) and c_P the `Precipitation_coefficient`. Here c_P = 400,000 m²: 40% of the 1 km² catchment. The plugin has no evapotranspiration, so c_P acts both as the unit conversion from depth to volume and as an effective-rainfall factor that absorbs all losses (mainly evapotranspiration). In a calibration it would be one of the fitted parameters.

**Slow store (`Storage Unit (Power-law)`).** Its latent variable is

  φ = a · S^b

with a = 2×10⁻¹¹ and b = 2. Draining to an outlet at φ = 0 through a link of transmissivity T, it is a nonlinear reservoir Q = T·a·S^b. With b = 2 the recession is fast at high storage and slows as the store empties. At the initial 50,000 m³, baseflow is 500 m³/day and the local recession rate dQ/dS is 0.02 1/day (a 50-day time scale). With b = 1 it would be a linear reservoir.

**Outlet (`Fixed Latent Variable Unit`).** Its latent variable is fixed (0 here) and it accepts any amount of water, like a fixed-head boundary.

**Network.** Rainfall → `Soil_store` → (`Direct_runoff`) → `Stream`, and `Soil_store` → (`Percolation`) → `Groundwater_store` → (`Baseflow`) → `Stream`. Because percolation is driven by φ_soil − φ_gw, it reverses whenever the fast store is drier, in potential terms, than the slow store: a simple representation of capillary rise or exchange in both directions.

**Time stepping.** The rainfall is an ordinary time series, not a precipitation source, so the setting `timestep_clamp_series = All time series` is used to make the solver stop at every change in rainfall. With the default (precipitation sources only) the solver can step across the start or end of a rain day and the rain actually applied differs from the record by about 1.5%.

## What to look for in the results

- **Two time scales.** Direct runoff rises within hours of rain and falls back within a few days. Baseflow changes over weeks. Between storms, flow is 400 to 1500 m³/day; on 30 September (118 mm of rain) it peaks at 18,800 m³/day.
- **Saturation behavior.** The fast store reaches 85% of capacity in the September storm. Because its potential grows as r/(1 − r), its outflows (direct runoff and percolation) jump by an order of magnitude when it is nearly full, and stay small otherwise.
- **Reversal.** For 13% of the year the fast store's potential is below the slow store's, and percolation runs upward (1,600 m³ in total, compared with 179,000 m³ downward).
- **Seasonality from storage.** Monthly baseflow is lowest in May and June (11 mm) and highest in October (25 mm) after the September storms refill the slow store.
- **Water balance.** Effective rainfall is 345,200 m³ (40% of 863 mm over 1 km²). Streamflow is 358,200 m³ (174,000 m³ direct runoff, 184,000 m³ baseflow); the stores lost 13,000 m³ over the year. The residual is about 30 m³ (0.01%).

## Assumptions and limitations

- The model is not calibrated. The parameters (capacity, scale factor, power-law coefficient and exponent, three transmissivities, precipitation coefficient and initial storages) are illustrative. In practice they are estimated from a rainfall–streamflow record with the calibration tools (see the Calibration and Uncertainty track).
- There is no evapotranspiration. All losses are folded into a constant precipitation coefficient, so the model cannot represent seasonal changes in the runoff ratio caused by evaporation.
- The latent variables are abstract potentials, not measurable heads. Only their differences matter, and only together with the transmissivities.
- The plugin's unit labels are not consistent with this usage: transmissivity is labeled m²/day, and the power-law store's storage is labeled in m while it is used here as a volume in m³. The numbers in this model are consistent among themselves (m³ and m³/day throughout).
- Daily rainfall is applied uniformly through each day, so sub-daily peaks are smoothed.
