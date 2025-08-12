import numpy as np
from src.utils.display import show_md

def calculate_shaft_diameter(M):
    """Calculate shaft diameter based on max bending moment."""
    M_max = np.max(np.abs(M))  # Nmm
    show_md(f"### 🧮 Max Bending Moment: {M_max:.2f} Nmm")

    sigma_allow = 100e6  # 100 MPa in N/m²
    M_Nm = M_max / 1e3  # Convert to Nm

    # Bending stress formula
    d_mm = ((32 * M_Nm) / (np.pi * sigma_allow)) ** (1 / 3) * 1000

    return round(d_mm, 2)
