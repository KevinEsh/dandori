import matplotlib.colors as mcolors


__colors = [tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(color)))
            for color in mcolors.CSS4_COLORS.values()]

# TODO: ponerle type a los procesos
__text_colors = {
    "STOP": "white",
    "PROCESS": "black",
    "MAINTAINANCE": "green",
    "QUALITY": "yellow",
}

# TODO: ponerle type a los procesos
__face_colors = {
    "STOP": (0, 0, 0),
    "PROCESS": (0.5, 0.5, 0.5),
}


def get_facecolor(plan, alpha=0.6):
    if not plan.toSolve:
        return (0, 0, 0, alpha)
    index = abs(hash(plan.toSolve.name)) % len(__colors)
    # if plan.toSolve.id:
    #     code = plan.toSolve.id
    # elif plan.toSolve.name:
    #     code = plan.toSolve.name
    # code = abs(hash(code))
    return (*__colors[index], alpha)


def get_textcolor(plan) -> str:
    """Return the color of the plan's text according to whether is a stop or a process

    Args:
        plan (Plan): Current plan to plot

    Returns:
        str: Name of the color text
    """
    if plan:
        return "black"
    return "grey"
