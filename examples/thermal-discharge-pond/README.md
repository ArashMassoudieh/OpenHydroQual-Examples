---
title: Thermal Discharge to a Flow-Through Pond
track: wq
level: 1
status: ready
summary: A power plant starts discharging 20 MW of waste heat into a well-mixed pond fed by a river. The Heat constituent carries the water temperature, and the surface heat exchange with the air sets how much the pond warms. The response is checked against its exact solution.
plugins: [mass_transfer]
features: [Heat constituent, Heat input, Surface heat exchange, Energy balance, Analytical verification]
keywords: [heat, temperature, water temperature, thermal pollution, thermal discharge, waste heat, power plant, cooling water, cooling pond, energy balance, heat budget, heat capacity, surface heat exchange, equilibrium temperature, cstr, steady state, analytical solution, verification]
extra_files: [exact_temperature.csv]
components:
  Temperature: A Heat (temperature) constituent. Each block stores its heat content ρ·c_p·V·T (MJ) and reports the temperature T (°C). The volumetric heat capacity ρ·c_p is 4.186 MJ/m³/°C, the value for water.
  Pond: A well-mixed pond of 200,000 m³ with a 100,000 m² water surface (2 m deep). It receives 50,000 m³/day of river water at 15 °C, starts at 15 °C, and from day 10 receives the plant's waste heat through its time-variable heat input.
  Air_exchange: Surface heat exchange source attached to the Pond. Heat moves between the water and the air at K·A·(T_air − T), with K = 30 W/m²/°C, A = 100,000 m² and T_air = 20 °C.
  Downstream: The receiving river below the pond, a fixed-head boundary at 0 m that accepts the outflow. Its temperature is not part of the analysis.
  Outflow: Fixed flow of 50,000 m³/day from Pond to Downstream, equal to the inflow, so the pond volume stays at 200,000 m³. It carries heat out at ρ·c_p·Q·T.
inputs:
  plant_heat.csv: "Waste heat discharged by the power plant into the pond. Column 1: time (day); column 2: heat input (kW). 0 kW until day 10, then 20,000 kW (20 MW)."
plots:
  - title: Pond temperature
    ylabel: Temperature (°C)
    series:
      - {column: "Pond_Temperature:concentration", label: "Pond, OpenHydroQual"}
      - {file: "exact_temperature.csv", label: "Pond, exact", style: points}
    hlines: [{y: 20, label: "Air temperature"}, {y: 15, label: "Inflow temperature"}]
    caption: Before the plant starts the pond settles at 17.77 °C, between the inflow and air temperatures. The 20 MW discharge from day 10 raises it by 3.69 °C to 21.45 °C, with a time constant of 1.79 days.
  - title: Pond heat budget
    ylabel: Heat flow (TJ/day, 1 TJ = 10⁶ MJ)
    series:
      - {column: "Pond_Temperature:inflow_loading", label: "Carried in by the river", scale: 1.0e-6}
      - {column: "Pond_Temperature:heat_input", label: "Power plant waste heat", scale: 1.0e-6}
      - {column: "Pond_Temperature:external_source", label: "Exchange with the air (+ = gain)", scale: 1.0e-6}
      - {column: "Outflow_Temperature:masstransfer", label: "Carried out by the outflow", scale: 1.0e-6}
    caption: At first the pond gains heat from the warmer air. Once the plant runs, the pond is warmer than the air and loses heat through its surface, which removes more than a fifth of the plant's heat.
---

## What this model represents

A power plant or industrial facility discharges its waste heat into a pond that a river flows through. The question is how much warmer the pond, and the water leaving it, becomes. That depends on three things: how much heat is added, how fast the flow carries heat away, and how much heat the pond exchanges with the air through its surface.

The pond is treated as completely mixed. Its temperature is carried by a **Heat (temperature)** constituent, which keeps an energy balance in place of a mass balance. The example runs 10 days without the plant, to show the natural temperature of the pond, then switches on a 20 MW discharge. With a constant air temperature the problem has an exact solution, so the example also verifies the heat transport, the heat input and the surface heat exchange in OpenHydroQual.

## How it works

**Water.** The Pond is a `Reactor` block with a constant inflow Q = 50,000 m³/day. The Outflow link removes the same flow, so the volume stays at V = 200,000 m³ and the hydraulic residence time is V/Q = 4 days.

**Heat content and temperature.** For the Heat constituent, the state of each block is its heat content E = ρ·c_p·V·T (MJ), and the temperature it reports is

  T = E / (ρ·c_p·V)

with ρ·c_p = 4.186 MJ/m³/°C (the constituent property `volumetric_heat_capacity`). Because ρ·c_p is constant, heat moves exactly like the mass of a dissolved substance, with ρ·c_p·T in the place of the concentration.

**Heat flows into and out of the pond** (MJ/day):

- carried in by the river: ρ·c_p·T_in·Q, with T_in = 15 °C (`inflow_loading`)
- added by the plant: 86.4·H, with H in kW from `plant_heat.csv` (`heat_input`; 1 kW = 86.4 MJ/day)
- exchanged with the air: 0.0864·K·A·(T_air − T), with K in W/m²/°C (`Air_exchange`, reported as `external_source`; positive when the pond gains heat)
- carried out by the outflow: ρ·c_p·Q·T (`Outflow` link, advective heat transfer of the upstream block)

so the energy balance of the pond is

  ρ·c_p·V·dT/dt = ρ·c_p·Q·(T_in − T) + 86.4·H + 0.0864·K·A·(T_air − T)

**Exact solution.** Write a = ρ·c_p·Q = 209,300 MJ/day/°C (heat carried away by the flow per degree) and b = 0.0864·K·A = 259,200 MJ/day/°C (surface exchange per degree). For constant inputs the temperature relaxes exponentially toward

  T_eq = (a·T_in + 86.4·H + b·T_air) / (a + b)

with the time constant

  τ = ρ·c_p·V / (a + b) = 1.787 days

Without the plant, T_eq = 17.77 °C. With H = 20,000 kW, T_eq = 21.45 °C, a rise of 86.4·H / (a + b) = 3.69 °C. The file `exact_temperature.csv` tabulates the two exponential segments (starting from 15 °C at day 0 and from the computed day-10 temperature at day 10) every 0.2 days.

**Time stepping.** The run uses a fixed time step of 0.01 days (`max_timestep_increase_factor` = 1), small compared with τ.

## What to look for in the results

- **Agreement with theory.** The computed temperature lies on the exact solution. The largest difference is about 0.004 °C, the time discretization error of the fully implicit (backward Euler) scheme, largest just after the heat is switched on.
- **The natural temperature.** Without the plant the pond does not stay at the 15 °C of the river. It settles at 17.77 °C, a weighted average of the inflow and air temperatures with weights a and b. The pond gains about 580,000 MJ/day from the air in this state.
- **The surface matters.** If the outflow were the only way out, the plant would warm the pond by 86.4·H / (ρ·c_p·Q) = 8.26 °C, the familiar ΔT = H/(ρ·c_p·Q) for a heated stream. The actual rise is 3.69 °C because the warmer pond also loses heat to the air: at the new steady state the surface exchange turns from a gain of 580,000 to a loss of about 377,000 MJ/day.
- **Faster response than the residence time.** The temperature responds with τ = 1.79 days, faster than the 4-day residence time, because surface exchange and outflow remove a temperature disturbance together (time constant ρ·c_p·V/(a + b), compared with V/Q for a dissolved tracer).
- **Heat budget.** At steady state the heat carried in by the river (3,139,500 MJ/day), plus the plant's 1,728,000 MJ/day, minus the 376,800 MJ/day lost to the air, equals the 4,490,300 MJ/day carried out by the outflow.

## Assumptions and limitations

- The pond is completely mixed and does not stratify. Deep ponds and lakes that receive warm water often form a warm surface layer, which loses heat to the air faster than this model predicts.
- Surface heat exchange is linearized: one coefficient K lumps radiation, evaporation and convection, and T_air acts as the equilibrium temperature the water relaxes toward. Both are held constant here. The source also accepts a time series of air temperature (`time_variable_air_temperature`) for daily or seasonal cycles.
- ρ·c_p is constant, and the plant's discharge is represented as heat added directly to the pond water, without a separate cooling-water stream.
- Flow, volume and inflow temperature are constant.
