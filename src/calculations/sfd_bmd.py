import numpy as np
import matplotlib.pyplot as plt

def plot_SFD_BMD(shaft, RA, RB):
    """Plot shear force and bending moment diagrams."""
    A, B = shaft["supports"]
    L = B - A
    dx = 1
    x = np.arange(0, L + 1, dx)
    V = np.zeros_like(x, dtype=float)
    M = np.zeros_like(x, dtype=float)

    for i, xi in enumerate(x):
        shear = RA
        moment = RA * xi

        if "point_loads" in shaft:
            for load in shaft["point_loads"]:
                if load["pos"] <= xi:
                    shear += load["magnitude"]
                    moment += load["magnitude"] * (xi - load["pos"])

        if "pulleys" in shaft:
            for pulley in shaft["pulleys"]:
                if pulley["pos"] <= xi:
                    shear += pulley["belt_force"]
                    moment += pulley["belt_force"] * (xi - pulley["pos"])

        V[i] = shear
        M[i] = moment

    fig, axs = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    axs[0].plot(x, V, 'r', lw=2)
    axs[0].axhline(0, color='black', lw=0.5)
    axs[0].set_ylabel("Shear Force (N)")
    axs[0].set_title("📉 Shear Force Diagram")
    axs[0].grid(True)

    axs[1].plot(x, M, 'b', lw=2)
    axs[1].axhline(0, color='black', lw=0.5)
    axs[1].set_ylabel("Bending Moment (Nmm)")
    axs[1].set_title("📈 Bending Moment Diagram")
    axs[1].set_xlabel("Position along Shaft (mm)")
    axs[1].grid(True)

    plt.tight_layout()
    plt.show()

    return M
