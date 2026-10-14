"""Write the .ohq model files of the shallow-lake (A) and stratified-lake (B) eutrophication examples.

Usage (from the examples/ folder of the OpenHydroQual-Examples repository):
    python shallow-lake-eutrophication/results/gen.py
The model files are plain text and can also be edited by hand; this script only documents how they were made.
"""
import os, sys

EX = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# name: (value, description) ; all ReactionParameter with Arrhenius_factor=1
PARAMS = [
    ("mu_max", 2.5), ("theta_g", 1.066), ("K_I", 30), ("K_N", 0.03), ("K_P", 0.005), ("K_NH", 0.025),
    ("k_bg", 0.8), ("k_chl", 0.016), ("chl_C", 25),
    ("a_NC", 0.176), ("a_PC", 0.0244), ("r_OC", 2.67), ("r_ON", 4.57), ("a_dn", 0.933),
    ("k_resp", 0.15), ("k_mort", 0.12), ("theta_a", 1.08),
    ("k_C", 0.1), ("k_ON", 0.05), ("k_OP", 0.07), ("theta_m", 1.08), ("K_O", 0.5), ("K_NOx", 0.1), ("f_an", 0.3),
    ("k_nit", 0.1), ("theta_n", 1.08), ("K_O_nit", 1.0),
    ("k_sorb", 0.0001), ("K_Fe", 1.0), ("k_rel", 0.012), ("k_odu", 1.0),
]
OVR = {}

T = "theta_m^(T_water-20)"
G = ("mu_max*theta_g^(T_water-20)"
     "*_log((K_I+PAR)/(K_I+PAR*_exp(0-(k_bg+k_chl*chl_C*Algae)*depth)))/((k_bg+k_chl*chl_C*Algae)*depth)"
     "*(NH3+NOx)/(K_N+NH3+NOx)*PO4/(K_P+PO4)*Algae")
P_NH = "(NH3*NOx/((K_NH+NH3)*(K_NH+NOx))+NH3*K_NH/((NH3+NOx)*(K_NH+NOx)))"
REACTIONS = [
    ("Growth_on_NH3", f"({G}*{P_NH})", dict(Algae="1", NH3="(0-a_NC)", PO4="(0-a_PC)", O2="r_OC")),
    ("Growth_on_NOx", f"({G}*(1-{P_NH}))", dict(Algae="1", NOx="(0-a_NC)", PO4="(0-a_PC)", O2="(r_OC+r_ON*a_NC)")),
    ("Algal_respiration", "(k_resp*theta_a^(T_water-20)*Algae*O2/(K_O+O2))", dict(Algae="-1", O2="(0-r_OC)", NH3="a_NC", PO4="a_PC")),
    ("Algal_mortality", "(k_mort*theta_a^(T_water-20)*Algae)", dict(Algae="-1", POC="1", ON="a_NC", OP="a_PC")),
    ("POC_aerobic_oxidation", f"(k_C*{T}*POC*O2/(K_O+O2))", dict(POC="-1", O2="(0-r_OC)")),
    ("Denitrification", f"(k_C*{T}*POC*K_O/(K_O+O2)*NOx/(K_NOx+NOx))", dict(POC="-1", NOx="(0-a_dn)", N2="a_dn")),
    ("POC_anaerobic_oxidation", f"(f_an*k_C*{T}*POC*K_O/(K_O+O2)*K_NOx/(K_NOx+NOx))", dict(POC="-1", ODU="r_OC")),
    ("ODU_oxidation", f"(k_odu*{T}*ODU*O2/(K_O+O2))", dict(ODU="-1", O2="-1")),
    ("Ammonification", f"(k_ON*{T}*ON)", dict(ON="-1", NH3="1")),
    ("OP_mineralization", f"(k_OP*{T}*OP)", dict(OP="-1", PO4="1")),
    ("Nitrification", "(k_nit*theta_n^(T_water-20)*NH3*O2/(K_O_nit+O2))", dict(NH3="-1", NOx="1", O2="(0-r_ON)")),
    ("P_sorption", "(k_sorb*Fe_ox*PO4*O2/(K_Fe+O2))", dict(PO4="-1", PIP="1")),
    ("P_release", f"(k_rel*{T}*PIP*K_Fe/(K_Fe+O2))", dict(PIP="-1", PO4="1")),
]
# name, type, settling velocity (m/day) for particles
CONST = [
    ("Algae", "Particle", 0.05), ("POC", "Particle", 0.25), ("ON", "Particle", 0.25), ("OP", "Particle", 0.25),
    ("PIP", "Particle", 0.3),
    ("PO4", "Constituent", None), ("NH3", "Constituent", None), ("NOx", "Constituent", None), ("O2", "Constituent", None), ("ODU", "Constituent", None),
    ("N2", "Immobile_Constituent", None), ("Fe_ox", "Immobile_Constituent", None),
]
NAMES = [c[0] for c in CONST]
INFLOW = ["PO4", "PIP", "OP", "NH3", "NOx", "ON", "POC", "O2"]
DISSOLVED_EX = dict(O2="0.2", PO4="0.02", NH3="0.02", NOx="0.02", ODU="0.02")


def u(v, unit):
    return f"{v}[{unit}]"


def concs(d):
    return ",".join(f"{n}:concentration={u(d.get(n, 0), 'g/m~^3')}" for n in NAMES)


def header(lines):
    lines += ["loadtemplate; filename = main_components.json",
              "addtemplate; filename = Pond_Plugin.json",
              "addtemplate; filename = groundwater.json",
              "addtemplate; filename = mass_transfer.json"]


def common(lines, wind="wind_speed.csv", temp="water_temperature.csv"):
    lines.append(f"create source;type=reaeration_Banks_Herrera,name=Reaeration,temperature={temp},theta=1.024,wind_speed={wind}")
    for n, typ, vs in CONST:
        if typ == "Particle":
            lines.append(f"create constituent;type=Particle,concentration=0[g/m~^3],constant_inflow_concentration=0[g/m~^3],external_mass_flow_timeseries=,external_source=,name={n},settling_velocity={vs}[m/day],stoichiometric_constant=0,time_variable_inflow_concentration=,turbidity_coefficient=0,turbidity_exponent=1")
        elif typ == "Constituent":
            lines.append(f"create constituent;type=Constituent,concentration=0[g/m~^3],constant_inflow_concentration=0[g/m~^3],diffusion_coefficient=0[m~^2/day],dispersivity=0[m],external_mass_flow_timeseries=,external_source=,name={n},stoichiometric_constant=0,time_variable_inflow_concentration=")
        else:
            lines.append(f"create constituent;type=Immobile_Constituent,concentration=0[g/m~^3],external_mass_flow_timeseries=,external_source=,name={n},stoichiometric_constant=0")
    for n, v in PARAMS:
        v = OVR.get(n, v)
        lines.append(f"create reaction_parameter;type=ReactionParameter,Arrhenius_factor=1,base_value={v},name={n},reference_temperature=20,temperature=")
    lines.append("create reaction_parameter;type=TimeDependent_ReactionParameter,name=T_water,value=")
    lines.append("create reaction_parameter;type=TimeDependent_ReactionParameter,name=PAR,value=")
    for name, rate, st in REACTIONS:
        sc = ",".join(f"{n}:stoichiometric_constant={st.get(n, '0')}" for n in NAMES)
        lines.append(f"create reaction;type=Reaction,{sc},name={name},rate_expression={rate}")


def inflow_props(suffix=""):
    s = []
    for n in INFLOW:
        f = f"tributary_{n}{suffix if n in ('PO4', 'PIP', 'OP') else ''}.csv"
        s.append(f"{n}:time_variable_inflow_concentration={f}")
    return ",".join(s)


def link_ex():
    return ",".join(f"{n}:exchange_velocity={v}[m/day]" for n, v in DISSOLVED_EX.items())


def obs(L, name, obj, expr):
    L.append(f"create observation;type=Observation,name={name},object={obj},expression={expr}")


CHL = "chl_C*Algae:concentration"
TP = "PO4:concentration+PIP:concentration+OP:concentration+a_PC*Algae:concentration"
TN = "NH3:concentration+NOx:concentration+ON:concentration+a_NC*Algae:concentration"
DOSAT = "14.652-0.41022*T_water:value+0.007991*T_water:value^2-0.000077774*T_water:value^3"


SYS = ["setvalue; object=system, quantity=alloutputfile, value=output.txt",
       "setvalue; object=system, quantity=simulation_start_time, value=0",
       "setvalue; object=system, quantity=simulation_end_time, value=365",
       "setvalue; object=system, quantity=initial_time_step, value=0.01",
       "setvalue; object=system, quantity=max_timestep_increase_factor, value=4",
       "setvalue; object=system, quantity=minimum_timestep, value=1e-06",
       "setvalue; object=system, quantity=write_interval, value=10"]

WATER0 = dict(Algae=0.1, POC=1.0, ON=0.3, OP=0.02, PIP=0.02, PO4=0.03, NH3=0.1, NOx=1.0, O2=12.0)
SED0 = dict(Algae=0, POC=200, ON=30, OP=4, PIP=40, PO4=0.15, NH3=2, NOx=0.1, O2=8, ODU=5, Fe_ox=5000)


def model_A(suffix=""):
    L = []
    header(L)
    common(L)
    A = 5.0e5
    L.append(f"create block;type=Pond,{concs(WATER0)},O2:external_source=Reaeration,{inflow_props(suffix)},"
             f"T_water:value=water_temperature.csv,PAR:value=par.csv,Evapotranspiration=,Precipitation=,"
             f"Storage=1263000[m~^3],_height=200,_width=200,alpha={A:.0f},alpha_multiplier=1,beta=1,bottom_elevation=0[m],"
             f"inflow=tributary_inflow.csv,name=Lake,x=400,y=200")
    L.append(f"create block;type=Groundwater cell,{concs(SED0)},T_water:value=water_temperature.csv,PAR:value=no_light.csv,"
             f"_height=200,_width=200,area={A:.0f}[m~^2],bottom_elevation=-0.1[m],depth=0.1[m],hydraulic_conductivity=0.0001[m/day],"
             f"inflow=,moisture_content=0.9,name=Sediment,porosity=0.9,specific_storage=0.01[1/m],x=400,y=600")
    L.append("create block;type=fixed_head,Storage=100000[m~^3],_height=200,_width=200,head=0[m],name=Outlet,x=850,y=200")
    L.append("create link;from=Lake,to=Outlet,type=wier,alpha=2940000,beta=1.5,crest_elevation=2.5[m],name=Outlet_weir")
    L.append(f"create link;from=Lake,to=Sediment,type=Time-Dependent flow,{link_ex()},area={A:.0f}[m~^2],flow=,length=0.05[m],name=Sediment_interface")
    obs(L, "Chl_a", "Lake", CHL)
    obs(L, "Total_P", "Lake", TP)
    obs(L, "Total_N", "Lake", TN)
    obs(L, "DO_saturation", "Lake", DOSAT)
    L += SYS
    return "\n".join(L) + "\n"


def model_B(suffix=""):
    L = []
    header(L)
    common(L)
    Ae, Ah = 5.0e5, 3.0e5
    L.append(f"create block;type=Pond,{concs(WATER0)},O2:external_source=Reaeration,{inflow_props(suffix)},"
             f"T_water:value=water_temperature.csv,PAR:value=par.csv,Evapotranspiration=,Precipitation=,"
             f"Storage=2027000[m~^3],_height=200,_width=200,alpha={Ae:.0f},alpha_multiplier=1,beta=1,bottom_elevation=8[m],"
             f"inflow=tributary_inflow.csv,name=Epilimnion,x=400,y=100")
    L.append(f"create block;type=Pond,{concs(WATER0)},"
             f"T_water:value=hypolimnion_temperature.csv,PAR:value=par_hypolimnion.csv,Evapotranspiration=,Precipitation=,"
             f"Storage=2400000[m~^3],_height=200,_width=200,alpha={Ah:.0f},alpha_multiplier=1,beta=1,bottom_elevation=0[m],"
             f"inflow=,name=Hypolimnion,x=400,y=450")
    L.append(f"create block;type=Groundwater cell,{concs(SED0)},T_water:value=hypolimnion_temperature.csv,PAR:value=no_light.csv,"
             f"_height=200,_width=200,area={Ah:.0f}[m~^2],bottom_elevation=-0.1[m],depth=0.1[m],hydraulic_conductivity=0.0001[m/day],"
             f"inflow=,moisture_content=0.9,name=Sediment,porosity=0.9,specific_storage=0.01[1/m],x=400,y=800")
    L.append("create block;type=fixed_head,Storage=100000[m~^3],_height=200,_width=200,head=8[m],name=Outlet,x=850,y=100")
    L.append("create link;from=Epilimnion,to=Outlet,type=wier,alpha=2940000,beta=1.5,crest_elevation=12[m],name=Outlet_weir")
    L.append(f"create link;from=Epilimnion,to=Hypolimnion,type=Time-Dependent flow,area={Ae:.0f}[m~^2],flow=vertical_exchange.csv,length=6[m],name=Exchange_down")
    L.append(f"create link;from=Hypolimnion,to=Epilimnion,type=Time-Dependent flow,area=1e-09[m~^2],flow=vertical_exchange.csv,length=6[m],name=Exchange_up")
    L.append(f"create link;from=Hypolimnion,to=Sediment,type=Time-Dependent flow,{link_ex()},area={Ah:.0f}[m~^2],flow=,length=0.05[m],name=Sediment_interface")
    obs(L, "Epi_chl_a", "Epilimnion", CHL)
    obs(L, "Epi_total_P", "Epilimnion", TP)
    obs(L, "Hypo_total_P", "Hypolimnion", TP)
    obs(L, "Epi_DO_saturation", "Epilimnion", DOSAT)
    L += SYS
    return "\n".join(L) + "\n"


def main_A():
    out = os.path.join(EX, "shallow-lake-eutrophication")
    open(os.path.join(out, "shallow_lake.ohq"), "w").write(model_A())
    open(os.path.join(out, "shallow_lake_p_load_50pct.ohq"), "w").write(model_A("_50pct"))


def main_B():
    out = os.path.join(EX, "stratified-lake-eutrophication")
    open(os.path.join(out, "stratified_lake.ohq"), "w").write(model_B())
    open(os.path.join(out, "stratified_lake_p_load_50pct.ohq"), "w").write(model_B("_50pct"))

    out = os.path.join(EX, "shallow-lake-eutrophication")
    open(os.path.join(out, "shallow_lake.ohq"), "w").write(model_A())
    open(os.path.join(out, "shallow_lake_p_load_50pct.ohq"), "w").write(model_A("_50pct"))


if __name__ == "__main__":
    main_A()
    main_B()
