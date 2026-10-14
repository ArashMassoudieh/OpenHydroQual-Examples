---
title: Snowpack Accumulation and Melt
track: hydro
level: 1
status: ready
summary: A 1 km² catchment through a cold-region winter, from 1 November to 30 April. Precipitation is split into rain and snow by air temperature, snow accumulates as snow water equivalent, and a degree-day model releases it as spring melt runoff.
plugins: [snowmelt]
features: [Rain/snow partition, Degree-day melt, Snow water equivalent, Seasonal runoff timing]
keywords: [snow, snowmelt, snowpack, degree day, temperature index, swe, snow water equivalent, rain snow partition, phase transition, air temperature, cold region, winter, spring melt, freshet, rain on snow, runoff timing, mountain hydrology]
components:
  Air_temperature: Daily air temperature (°C) read from `air_temperature.csv`. Drives melt in the snowpack.
  Snowfall: The solid share of the precipitation in `precipitation.csv`. All of it is snow at or below −1 °C, none above 1 °C, with a linear transition in between. Delivered to the snowpack as a volume rate over the snowpack area.
  Rainfall: The liquid share of the same precipitation series, using the same temperature transition. Delivered directly to the land surface. Rain and snow fractions always add to one, so no precipitation is lost or double counted.
  Snowpack: Snow water equivalent (SWE) store over the whole 1 km² catchment. Gains snowfall and loses melt. Degree-day factor 3 mm/day/°C, melt threshold 0 °C, no snow at the start.
  Land_surface: The 1 km² ground surface that collects rain and melt water. Every drop that reaches it runs off (runoff coefficient 1, no infiltration, no depression storage). Sheet flow toward the outlet follows Manning's equation (width 1000 m, slope 0.02, n = 0.1).
  Outlet: Fixed-head boundary at the catchment outlet. Its storage starts at zero and accumulates all runoff, so it is a running total of water yield.
  Snowmelt: Degree-day melt from the snowpack to the land surface. Limited by the water stored in the pack.
  Runoff: Overland flow from the land surface to the outlet.
inputs:
  air_temperature.csv: 'Synthetic daily mean air temperature (°C) versus time (days since 1 November). A seasonal cycle with a mid-January minimum near −10 °C plus random day-to-day weather anomalies. Two columns, no header.'
  precipitation.csv: 'Synthetic daily precipitation. Three columns, no header: interval start (days), interval end (days), water-equivalent depth in the interval (m). 64 wet days and 334 mm in 181 days.'
plots:
  - title: Air temperature
    ylabel: Temperature (°C)
    series:
      - {column: "Air_temperature_timeseries", label: "Air temperature"}
    caption: Below freezing for most of December to early March, with brief thaws. Spring warming starts in early March (around day 125).
  - title: Rain and snow
    ylabel: Rate (m³/day; 1000 m³/day = 1 mm/day)
    series:
      - {column: "Snowpack_Snowfall", label: "Snowfall into the snowpack"}
      - {column: "Land_surface_Precipitation", label: "Rainfall onto the land surface"}
    caption: The same precipitation record split by temperature. Autumn and late-spring storms fall as rain; winter storms fall as snow.
  - title: Snow water equivalent
    ylabel: SWE (m)
    series:
      - {column: "Snowpack_SWE", label: "SWE"}
    caption: The snowpack builds from mid-November to a peak of 189 mm around 11 March (day 131), then melts out in about three and a half weeks.
  - title: Melt and runoff
    ylabel: Flow (m³/day; 1000 m³/day = 1 mm/day)
    series:
      - {column: "Snowmelt_flow", label: "Snowmelt"}
      - {column: "Runoff_flow", label: "Runoff at the outlet"}
    caption: Autumn rain produces short runoff events. In winter runoff almost stops. Most of the season's water leaves in the spring melt pulse between days 125 and 155.
  - title: Cumulative water yield
    ylabel: Volume (m³)
    series:
      - {column: "Outlet_Storage", label: "Total runoff at the outlet"}
    caption: Water yield stays flat through the winter while precipitation is stored as snow, then rises steeply during the melt. The final value equals the total precipitation (334,000 m³ = 334 mm).
---

## What this model represents

In cold regions much of the winter precipitation does not run off when it falls. It is stored as snow and released weeks or months later, when the air warms in spring. The timing of runoff is therefore controlled by temperature as much as by precipitation. This model follows one winter (1 November to 30 April, days 0 to 181) on a 1 km² catchment with synthetic but realistic weather for a cold continental site: monthly mean temperatures of −1, −8, −10, −5, 0 and +10 °C from November to April, and 334 mm of precipitation.

The model is a minimal temperature-index (degree-day) snow model, the approach used in most operational and conceptual watershed models (for example HBV, SWAT and SRM). It shows the three steps that every such model has: partition precipitation into rain and snow, store the snow as water equivalent, and melt it at a rate set by air temperature.

## How it works

**Rain and snow.** Both precipitation sources read the same file. Each computes an effective temperature T = T_air + temperature_offset (offset 0 here) and splits the precipitation with a linear transition between T_s = −1 °C and T_r = +1 °C:

  f_rain = min(max((T − T_s)/(T_r − T_s), 0), 1),  f_snow = 1 − f_rain

A source delivers coefficient × series value × rate, where the coefficient is the area of the receiving block and the rate is f_rain or f_snow. `Rainfall` is assigned to the land surface and `Snowfall` to the snowpack, so the snowpack receives P·f_snow·A and the land surface P·f_rain·A, where P is the precipitation intensity (m/day) and A = 10⁶ m².

**Snowpack.** The snowpack stores snow as a water-equivalent volume V_snow, with SWE = V_snow/A. Its balance is

  dV_snow/dt = P·f_snow·A − Q_melt

**Melt.** The `Snowmelt` link moves water from the snowpack to the land surface at the degree-day rate

  Q_melt = A · DDF · max(T − T_m, 0)

with DDF = 0.003 m/day/°C and T_m = 0 °C. Every degree above freezing melts 3 mm of SWE per day. The link is storage limited: once the pack is empty, melt stops even if it is warm.

**Land surface and outlet.** The land surface is a `Catchment` block. It receives rain and melt and drains to the outlet with Manning's equation for sheet flow,

  Q = 86400 · (W/n) · S^0.5 · max(d − d_s, 0)^(5/3)  (m³/day)

where d is the water depth on the surface (Storage/area), W the width, S the slope, n the roughness and d_s the depression storage (0 here). With a runoff coefficient of 1 every drop reaching the surface becomes runoff. The outlet is a fixed-head block whose storage starts at zero, so it records the cumulative yield.

Because the area is 1 km², a flow of 1000 m³/day equals 1 mm/day of water depth over the catchment.

## What to look for in the results

- **Partition.** Of the 334 mm of precipitation, 228 mm falls as snow and 106 mm as rain. November and late-April storms are rain; December to March storms are almost all snow.
- **Accumulation.** A first thin snow cover (days 5 to 10) melts during a warm rain storm on day 11. The lasting pack starts around day 18. SWE then grows in steps, one per storm, and reaches its maximum of 189 mm around day 131 (11 March). Short thaws melt only 9 mm of snow before day 120.
- **Delayed runoff.** About 52 mm runs off in November, mainly from a rain storm on day 10. From early December to early March almost no water leaves the catchment, even though about 190 mm of precipitation falls between days 30 and 130.
- **Spring freshet.** Once temperatures stay above 0 °C, melt rates reach 23 mm/day (day 150) and the pack is gone by day 155 (early April). Between days 125 and 155 about 245 mm leaves the catchment, almost three quarters of the season's yield.
- **Water balance.** At the end of the run the snowpack is empty, 0.5 mm is still on the land surface, and the outlet has received 333.5 mm. Snowfall plus rainfall is 334.0 mm, so the balance closes.

## Assumptions and limitations

- The weather is synthetic. Temperature and precipitation are uniform over the catchment.
- This is a temperature-index model. It does not represent the energy balance (radiation, wind, humidity), cold content, refreezing, liquid water held in the pack, sublimation, canopy interception or wind redistribution of snow.
- The degree-day factor and transition temperatures are typical values, not calibrated. In practice the degree-day factor varies from about 2 to 6 mm/day/°C and often increases through the melt season.
- Snow covers the whole catchment whenever SWE is above zero. There is no snow-covered-area depletion curve.
- The land surface does not infiltrate or evaporate water, so all precipitation eventually becomes runoff. To study infiltration and soil storage, connect the melt to a soil-based unit such as a hydrologic response unit; the `snowmelt` plugin has pervious and impervious melt links for that purpose.
- `temperature_offset` can shift the temperature of a higher or lower surface (lapse-rate correction). Apply the same offset to the snowpack and both precipitation sources.
