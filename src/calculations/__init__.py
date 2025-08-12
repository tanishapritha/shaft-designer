import numpy as np
import pandas as pd

def torque_from_power(P_kw, rpm):
    """Return torque in N·m. P in kW, rpm in rev/min"""
    if rpm <= 0:
        return 0.0
    return 9550.0 * P_kw / rpm

def gear_forces(T_nm, gear_diameter_mm, pressure_angle_deg=20):
    """Return tangential and radial forces on gear."""
    d_m = gear_diameter_mm / 1000.0
    if d_m <= 0:
        return 0.0, 0.0
    Ft = 2.0 * T_nm / d_m
    phi = np.deg2rad(pressure_angle_deg)
    Fr = Ft * np.tan(phi)
    return Ft, Fr

def pulley_tensions(T_nm, pulley_diameter_mm, tension_ratio=2.0):
    """
    Calculate tight side (T1) and slack side (T2) belt tensions.
    Args:
        T_nm (float): Torque in Nm.
        pulley_diameter_mm (float): Diameter of pulley in mm.
        tension_ratio (float): Ratio T1 / T2, must be > 1.
    Returns:
        (T1, T2): Tuple of tensions in Newtons.
    Raises:
        ValueError: If tension_ratio <= 1 or pulley diameter <= 0.
    """
    if pulley_diameter_mm <= 0:
        raise ValueError("Pulley diameter must be positive.")
    if tension_ratio <= 1:
        raise ValueError("Tension ratio must be greater than 1.")

    radius_m = pulley_diameter_mm / 1000.0 / 2  # convert mm to meters and get radius
    T2 = T_nm / (radius_m * (tension_ratio - 1))
    T1 = tension_ratio * T2
    return T1, T2


def point_load_moment(load_N, position_m):
    """Return bending moment for a point load."""
    return load_N * position_m

def combine_bending_moments(moments_list):
    """Return sum of bending moments."""
    return float(np.sum(moments_list))

def diameter_from_torsion(T_nm, sy_mpa, fos):
    """From tau = 16T / (pi d^3)"""
    if sy_mpa <= 0 or fos <= 0:
        return None
    tau_allow_pa = (sy_mpa * 1e6) / fos
    d_m = (16.0 * T_nm / (np.pi * tau_allow_pa)) ** (1.0 / 3.0)
    return d_m

def diameter_from_bending(Mb_nm, sy_mpa, fos):
    """From sigma = 32M / (pi d^3)"""
    if sy_mpa <= 0 or fos <= 0:
        return None
    sigma_allow_pa = (sy_mpa * 1e6) / fos
    d_m = (32.0 * Mb_nm / (np.pi * sigma_allow_pa)) ** (1.0 / 3.0)
    return d_m

def diameter_from_combined(Mb_nm, T_nm, sy_mpa, fos, Kb=1.0, Kt=1.0):
    """
    ASME-like: d = [ (16/(pi tau_allow)) * sqrt((Kb*Mb)^2 + (Kt*T)^2 ) ]^(1/3)
    """
    if sy_mpa <= 0 or fos <= 0:
        return None
    tau_allow_pa = (sy_mpa * 1e6) / fos
    term = np.sqrt((Kb * Mb_nm)**2 + (Kt * T_nm)**2)
    d_m = ((16.0 / (np.pi * tau_allow_pa)) * term) ** (1.0 / 3.0)
    return d_m

def round_to_standard(d_m, shaft_sizes_df):
    """Round shaft diameter to the next standard size in the dataframe."""
    if d_m is None or d_m <= 0:
        return None
    d_mm = d_m * 1000.0
    sizes = np.array(shaft_sizes_df['Size (mm)'].values, dtype=float)
    larger = sizes[sizes >= d_mm]
    if larger.size > 0:
        return float(larger[0]) / 1000.0  # Return in meters
    else:
        return float(sizes.max()) / 1000.0  # Max available size
