# src/visuals/visuals.py
import matplotlib.pyplot as plt
import numpy as np

def shaft_diagram(length=1.0, supports=None, loads=None):
    """
    Plot a simple shaft layout with supports and loads.
    length: total shaft length (m)
    supports: list of positions (m) for supports
    loads: list of tuples (position, magnitude) in N
    """
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot([0, length], [0, 0], 'k-', lw=4)  # shaft line

    # supports
    if supports:
        for s in supports:
            ax.plot(s, 0, 'gv', markersize=10, label="Support")

    # loads
    if loads:
        for pos, mag in loads:
            ax.arrow(pos, 0.1, 0, mag/abs(mag)*0.3, 
                     head_width=0.02, head_length=0.05, fc='r', ec='r')
            ax.text(pos, 0.5 if mag > 0 else -0.5, f"{mag} N", 
                    ha='center', fontsize=8)

    ax.set_xlim(-0.1, length+0.1)
    ax.set_ylim(-1, 1)
    ax.axis('off')
    return fig


def moment_diagram(length=1.0, moments=None):
    """
    Plot a bending moment diagram.
    moments: list of tuples (position, moment_value in Nm)
    """
    x = np.linspace(0, length, 100)
    y = np.zeros_like(x)

    if moments:
        for pos, m in moments:
            idx = np.argmin(abs(x - pos))
            y[idx:] += m  # simple step effect

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(x, y, 'b-', lw=2)
    ax.axhline(0, color='black', lw=1)
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Moment (Nm)")
    ax.set_title("Bending Moment Diagram")
    return fig


def torque_diagram(length=1.0, torques=None):
    """
    Plot a torque diagram.
    torques: list of tuples (position, torque_value in Nm)
    """
    x = np.linspace(0, length, 100)
    y = np.zeros_like(x)

    if torques:
        for pos, t in torques:
            idx = np.argmin(abs(x - pos))
            y[idx:] += t

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(x, y, 'm-', lw=2)
    ax.axhline(0, color='black', lw=1)
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Torque (Nm)")
    ax.set_title("Torque Diagram")
    return fig



def gear_side_view(diameter_mm=200, pressure_angle_deg=20):
    """
    Side view schematic of a gear showing pitch diameter and pressure angle.
    diameter_mm: gear pitch diameter in mm
    pressure_angle_deg: pressure angle in degrees
    """
    fig, ax = plt.subplots(figsize=(4,4))
    radius = diameter_mm / 2 / 10  # scale down for plot (cm)
    circle = plt.Circle((0, 0), radius, fill=False, color='blue', lw=2)
    ax.add_patch(circle)

    # Draw center line
    ax.plot([-radius*1.2, radius*1.2], [0,0], 'k--', lw=1)

    # Draw pressure angle lines (two lines at +/- pressure angle from horizontal at outer radius)
    angle_rad = np.deg2rad(pressure_angle_deg)
    x_outer = radius * np.cos(angle_rad)
    y_outer = radius * np.sin(angle_rad)
    ax.plot([0, x_outer], [0, y_outer], 'r-', lw=2, label="Pressure Angle")
    ax.plot([0, x_outer], [0, -y_outer], 'r-', lw=2)

    # Annotations
    ax.text(0, -radius*1.3, f"Pitch Diameter = {diameter_mm} mm", ha='center', fontsize=10)
    ax.text(radius*0.5, radius*0.5, f"Pressure Angle = {pressure_angle_deg}°", color='red', fontsize=10)

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Gear Side View")
    return fig


def pulley_side_view(diameter_mm=300, belt_tension_ratio=2.0):
    """
    Side view schematic of a pulley showing diameter and belt tensions.
    diameter_mm: pulley diameter in mm
    belt_tension_ratio: T1/T2 ratio
    """
    fig, ax = plt.subplots(figsize=(4,4))
    radius = diameter_mm / 2 / 10  # scale down for plot (cm)
    circle = plt.Circle((0, 0), radius, fill=False, color='green', lw=2)
    ax.add_patch(circle)

    # Draw center line
    ax.plot([-radius*1.2, radius*1.2], [0,0], 'k--', lw=1)

    # Show belt tensions as arrows tangential to pulley
    arrow_length = radius * 0.8
    # T1 arrow - clockwise at top
    ax.arrow(0, radius, arrow_length*0.6, 0, head_width=0.05*radius, head_length=0.1*radius, fc='red', ec='red')
    ax.text(arrow_length*0.7, radius*1.1, f"T1", color='red', fontsize=10)

    # T2 arrow - counter-clockwise at bottom
    ax.arrow(0, -radius, -arrow_length*0.6, 0, head_width=0.05*radius, head_length=0.1*radius, fc='blue', ec='blue')
    ax.text(-arrow_length*1.3, -radius*1.1, f"T2", color='blue', fontsize=10)

    # Annotations
    ax.text(0, -radius*1.3, f"Pulley Diameter = {diameter_mm} mm", ha='center', fontsize=10)
    ax.text(0, radius*1.3, f"Belt Tension Ratio = {belt_tension_ratio:.2f}", ha='center', fontsize=10, color='purple')

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Pulley Side View")
    return fig


import matplotlib.pyplot as plt

def shaft_overview_diagram(length=1.0, gears=None, pulleys=None):
    """
    Plot a simple shaft overview with gears and pulleys positioned,
    annotated with key parameters (diameter or Ft for gears, diameter and tension ratio for pulleys).
    Parameters:
        length: shaft length in meters
        gears: list of dicts with keys: position (m), diameter or Ft, pressure_angle
        pulleys: list of dicts with keys: position (m), diameter, belt_tension_ratio
    """
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot([0, length], [0, 0], 'k-', lw=6)  # shaft baseline
    
    # Plot gears
    if gears:
        for i, g in enumerate(gears):
            pos = g['position']
            # marker shape based on if diameter known or Ft known
            if 'diameter' in g:
                size = g['diameter'] / 1000  # scale down for plot
                ax.plot(pos, 0, marker='s', markersize=12, color='blue')
                label = f"Gear {i+1}\nD={g['diameter']}mm"
            else:
                ax.plot(pos, 0, marker='o', markersize=10, color='cyan')
                label = f"Gear {i+1}\nFt={g['Ft']:.0f}N"
            ax.text(pos, 0.2, label, ha='center', fontsize=8, color='navy')

    # Plot pulleys
    if pulleys:
        for i, p in enumerate(pulleys):
            pos = p['position']
            size = p['diameter'] / 1000  # scale down
            ax.plot(pos, 0, marker='^', markersize=14, color='orange')
            label = f"Pulley {i+1}\nD={p['diameter']}mm\nBTR={p['belt_tension_ratio']:.2f}"
            ax.text(pos, -0.25, label, ha='center', fontsize=8, color='darkorange')

    ax.set_xlim(-0.05 * length, length + 0.05 * length)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    ax.set_title("Shaft Overview (positions & specs)", fontsize=12)
    fig.tight_layout()
    return fig
