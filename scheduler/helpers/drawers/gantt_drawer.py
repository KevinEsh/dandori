import numpy as np
import matplotlib.pyplot as plt
from pydash import group_by
from scheduler.models import Program
from scheduler.helpers import datetools
from scheduler.helpers.drawers.labels import get_label_3
from scheduler.helpers.drawers.colors import get_facecolor
from scheduler.helpers.drawers.globals import CONFIG_GANTT, MAX_GANTT_SIZE


def plot_gantt(program: Program, imagename: str = "gantt.jpg", scale: str = "hours", **options: str) -> None:
    """Plot and save a gantt chart image with matplotlib for a GraphQLType program

    Args:
        program (GraphQLType): Program with plans to be ploted
        imagename (str, optional): Name of the image to save the gantt chart. Defaults to "gantt.jpg".
        scale (str, optional): Time scale for x axe. Defaults to "hours".
    """
    CONFIG_GANTT.update(options)
    gaps = CONFIG_GANTT["gaps"]

    plans_by_resource = group_by(program.plans, "resource.name")
    extension = datetools.to_int(program.endAt, program.startAt, scale)
    num_resources = len(plans_by_resource)

    fig = plt.figure(
        figsize=(
            min(extension//7, MAX_GANTT_SIZE),
            min(num_resources, MAX_GANTT_SIZE)
        )
    )
    ax = fig.add_subplot(111)
    # minor_ticks = np.arange(0, extension+1, 0.6)  # TODO
    # ax.set_xticks(minor_ticks)
    ax.xaxis.grid()

    for row, (name, plans) in enumerate(plans_by_resource.items()):
        if not name or not plans:
            continue

        for plan in plans:
            # Calculating interval
            start = datetools.to_int(plan.startAt, program.startAt, scale)
            end = datetools.to_int(plan.endAt, program.startAt, scale)
            middle_x = start + 0.5  # (start + end) / 2
            middle_y = row + 0.2

            # Coloring and labeling by order
            CONFIG_GANTT["box"]["facecolor"] = get_facecolor(plan)
            label = get_label_3(plan)

            plt.fill_between([start, end-gaps[0]], [row, row],
                             [row+1-gaps[1], row+1-gaps[1]], **CONFIG_GANTT["box"])
            plt.text(middle_x, middle_y, label, **CONFIG_GANTT["text"])

    ax.set_yticks(np.arange(0.5, num_resources, 1.0))
    ax.set_yticklabels(plans_by_resource.keys())
    plt.xlabel(scale)

    plt.savefig(imagename)
    plt.close()
