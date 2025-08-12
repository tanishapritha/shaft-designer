def calculate_reactions(shaft_input, supports=(0, 1000)):
    """Calculate support reactions for a simply supported shaft."""
    A, B = supports
    L = B - A

    total_vertical = 0
    total_moment_B = 0

    for el in shaft_input["elements"]:
        x = el["position"]
        typ = el["type"]

        if typ == "load":
            F = el["value"]
            total_vertical += F
            total_moment_B += F * (B - x)

        elif typ == "pulley":
            F = el.get("belt_force", 0)
            total_vertical += F
            total_moment_B += F * (B - x)

    RA = total_moment_B / L
    RB = total_vertical - RA

    return round(RA, 2), round(RB, 2)
