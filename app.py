import streamlit as st
import pandas as pd
import math
from src.calculations import (
    torque_from_power,
    gear_forces,
    pulley_tensions,
    point_load_moment,
    combine_bending_moments,
    diameter_from_torsion,
    diameter_from_bending,
    diameter_from_combined,
    round_to_standard
)
from src.visuals.visuals import (
    shaft_diagram,
    moment_diagram,
    torque_diagram,
    gear_side_view,
    pulley_side_view,
    shaft_overview_diagram
)


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# local_css("styles.css")

# Load data with caching
@st.cache_data
def load_materials():
    return pd.read_csv("data/materials.csv")

@st.cache_data
def load_shaft_sizes():
    return pd.read_csv("data/shaft_sizes.csv")

materials_df = load_materials()
shaft_sizes_df = load_shaft_sizes()

st.set_page_config(page_title="Shaft Diameter Tutor", layout="wide")
st.title("🔧 Shaft Diameter Interactive Designer")
st.markdown("Input parameters in the sidebar and see the results and diagrams below.")

with st.sidebar:
    st.header("Input Parameters")
    material = st.selectbox("Material", materials_df["Material"].tolist())
    sy = materials_df.loc[materials_df["Material"] == material, "Sy (MPa)"].values[0]
    fos = st.number_input("Factor of Safety", 1.0, 10.0, 2.0, 0.1,
                          help="Higher value means safer but larger shaft diameter.")
    shaft_length = st.number_input("Shaft Length (mm)", 1.0, 10000.0, 1000.0)
    power_kW = st.number_input("Power (kW)", 0.0, 10000.0, 15.0)
    rpm = st.number_input("Speed (RPM)", 1.0, 10000.0, 960.0)
    num_gears = st.number_input("Number of Gears", 0, 10, 1, 1)
    num_pulleys = st.number_input("Number of Pulleys", 0, 10, 1, 1)
    additional_bm = st.number_input("Additional Bending Moment (N·mm)", 0.0)
    additional_tm = st.number_input("Additional Torsional Moment (N·m)", 0.0)

# Collect gears input
gears = []
for i in range(num_gears):
    with st.container():
        st.markdown(f'<div class="card"><h4>Gear #{i+1} Configuration</h4></div>', unsafe_allow_html=True)
        specify_Ft = st.checkbox(f"Specify Gear #{i+1} Tangential Force Ft directly?", key=f"spec_ft_{i}")
        if specify_Ft:
            Ft = st.number_input(f"Gear #{i+1} Tangential Force Ft (N)", 0.0, 1e7, 1000.0, key=f"ft_{i}")
            pa = st.number_input(f"Gear #{i+1} Pressure Angle (°)", 0.0, 45.0, 20.0, key=f"pa_ft_{i}")
            pos = st.number_input(f"Gear #{i+1} Position from Left Bearing (mm)", 0.0, shaft_length, 200.0, key=f"pos_ft_{i}")
            gears.append({"Ft": Ft, "pressure_angle": pa, "position": pos})
        else:
            dia = st.number_input(f"Gear #{i+1} Diameter (mm)", 1.0, 10000.0, 200.0, key=f"dia_{i}")
            pa = st.number_input(f"Gear #{i+1} Pressure Angle (°)", 0.0, 45.0, 20.0, key=f"pa_dia_{i}")
            pos = st.number_input(f"Gear #{i+1} Position from Left Bearing (mm)", 0.0, shaft_length, 200.0, key=f"pos_dia_{i}")
            gears.append({"diameter": dia, "pressure_angle": pa, "position": pos})

# Collect pulleys input
pulleys = []
for i in range(num_pulleys):
    with st.container():
        st.markdown(f'<div class="card"><h4>Pulley #{i+1} Configuration</h4></div>', unsafe_allow_html=True)
        dia = st.number_input(f"Pulley #{i+1} Diameter (mm)", 1.0, 10000.0, 300.0, key=f"pdia_{i}")
        btr = st.number_input(f"Pulley #{i+1} Belt Tension Ratio (T1/T2)", 1.0, 10.0, 2.0, key=f"pbtr_{i}")
        pos = st.number_input(f"Pulley #{i+1} Position from Left Bearing (mm)", 0.0, shaft_length, 500.0, key=f"ppos_{i}")
        pulleys.append({"diameter": dia, "belt_tension_ratio": btr, "position": pos})



gear_positions_m = []
for g in gears:
    gear_positions_m.append({
        "position": g["position"] / 1000,
        "diameter": g.get("diameter"),
        "Ft": g.get("Ft"),
        "pressure_angle": g.get("pressure_angle", 20)
    })

pulley_positions_m = []
for p in pulleys:
    pulley_positions_m.append({
        "position": p["position"] / 1000,
        "diameter": p["diameter"],
        "belt_tension_ratio": p["belt_tension_ratio"]
    })

shaft_length_m = shaft_length / 1000

fig_overview = shaft_overview_diagram(length=shaft_length_m, gears=gear_positions_m, pulleys=pulley_positions_m)

with st.container():
    st.markdown('<div class="card"><h3>Shaft Overview</h3></div>', unsafe_allow_html=True)
    st.pyplot(fig_overview)



with st.spinner("Calculating shaft parameters..."):
    torque = torque_from_power(power_kW, rpm)

    Ft_total = 0.0
    Fr_total = 0.0
    M_gears = []

    for gear in gears:
        if "Ft" in gear:
            Ft = gear["Ft"]
            Fr = Ft * math.tan(math.radians(gear["pressure_angle"]))
        else:
            Ft, Fr = gear_forces(torque, gear["diameter"], gear["pressure_angle"])
        M = point_load_moment(Ft, gear["position"])
        M_gears.append(M)
        Ft_total += Ft
        Fr_total += Fr

    T1_total = 0.0
    T2_total = 0.0
    M_pulleys = []

    for pulley in pulleys:
        T1, T2 = pulley_tensions(torque, pulley["diameter"], pulley["belt_tension_ratio"])
        M = point_load_moment(T1 - T2, pulley["position"])
        M_pulleys.append(M)
        T1_total += T1
        T2_total += T2

    M_total = combine_bending_moments(M_gears + M_pulleys + [additional_bm])
    torque_total = torque + additional_tm

    d_torsion = diameter_from_torsion(torque_total, sy, fos)
    d_bending = diameter_from_bending(M_total, sy, fos)
    d_combined = diameter_from_combined(M_total, torque_total, sy, fos)
    final_d = round_to_standard(d_combined, shaft_sizes_df)

# Results card
with st.container():
    st.markdown('<div class="card"><h3>Results Summary</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Torque (N·m)", f"{torque_total:.2f}")
        st.metric("Total Tangential Force Ft (N)", f"{Ft_total:.2f}")
        st.metric("Total Radial Force Fr (N)", f"{Fr_total:.2f}")
        st.metric("Total Pulley Tension T1 (N)", f"{T1_total:.2f}")
        st.metric("Total Pulley Tension T2 (N)", f"{T2_total:.2f}")
    with col2:
        st.metric("Bending Moment (N·mm)", f"{M_total:.2f}")
        st.metric("Diameter from Torsion (mm)", f"{d_torsion:.2f}")
        st.metric("Diameter from Bending (mm)", f"{d_bending:.2f}")
        st.metric("Diameter from Combined (mm)", f"{d_combined:.2f}")
        st.success(f"Recommended Standard Shaft Diameter: **{final_d} mm**")

# Visual cards stacked vertically
def show_fig_card(title, fig):
    with st.container():
        st.markdown(f'<div class="card"><h3>{title}</h3></div>', unsafe_allow_html=True)
        st.pyplot(fig)

# Positions in meters for shaft diagrams
gear_positions_m = [g["position"] / 1000 for g in gears]
pulley_positions_m = [p["position"] / 1000 for p in pulleys]

# Shaft Diagram
supports = gear_positions_m + pulley_positions_m
loads = []
for i, g in enumerate(gears):
    if "Ft" in gears[i]:
        Ft = gears[i]["Ft"]
    else:
        Ft, _ = gear_forces(torque, g["diameter"], g["pressure_angle"])
    loads.append((gear_positions_m[i], Ft))
for i, p in enumerate(pulleys):
    T1, T2 = pulley_tensions(torque, p["diameter"], p["belt_tension_ratio"])
    loads.append((pulley_positions_m[i], T1 - T2))

fig_shaft = shaft_diagram(length=shaft_length_m, supports=supports, loads=loads)
show_fig_card("Shaft Diagram", fig_shaft)

if M_total > 0:
    moments = []
    for i, M in enumerate(M_gears):
        moments.append((gear_positions_m[i], M))
    for i, M in enumerate(M_pulleys):
        moments.append((pulley_positions_m[i], M))
    fig_moment = moment_diagram(length=shaft_length_m, moments=moments)
    show_fig_card("Moment Diagram", fig_moment)
else:
    st.info("No bending moments to display.")

if torque_total > 0:
    torques = [(0, torque_total)]
    fig_torque = torque_diagram(length=shaft_length_m, torques=torques)
    show_fig_card("Torque Diagram", fig_torque)
else:
    st.info("No torsional moments to display.")

if gears or pulleys:
    st.markdown('<div class="card"><h3>Side Views</h3></div>', unsafe_allow_html=True)

    items = []

    for i, g in enumerate(gears):
        if "diameter" in g:
            fig = gear_side_view(g["diameter"], g["pressure_angle"])
            items.append(("Gear Side View #" + str(i+1), fig))
        else:

            pass


    for i, p in enumerate(pulleys):
        fig = pulley_side_view(p["diameter"], p["belt_tension_ratio"])
        items.append(("Pulley Side View #" + str(i+1), fig))


    for i in range(0, len(items), 3):
        cols = st.columns(min(3, len(items) - i))
        for col, (title, fig) in zip(cols, items[i:i+3]):
            with col:
                st.markdown(f"### {title}")
                st.pyplot(fig, use_container_width=True)
else:
    st.info("No gears or pulleys configured for side views.")
