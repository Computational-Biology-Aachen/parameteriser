from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from scipy.stats import gaussian_kde

from parameteriser._utils import unwrap

__all__ = [
    "add_boxplot",
    "normalise",
    "plot_parameter_distribution",
    "plot_parameter_distributions",
    "savefig",
    "x_to_data",
    "y_to_data",
]

if TYPE_CHECKING:
    import pandas as pd
    from matplotlib.axes import Axes


def normalise(x: np.ndarray) -> np.ndarray:
    return x / np.sum(x)


def x_to_data(ax: Axes, val: float) -> float:
    return ax.transLimits.inverted().transform((val, 0))[0]


def y_to_data(ax: Axes, val: float) -> float:
    return ax.transLimits.inverted().transform((0, val))[1]


def add_boxplot(
    ax: Axes,
    data: pd.Series,
    color: str = "C0",
    offset: int = 0,
) -> None:
    _d = data.describe()
    iqr = _d["75%"] - _d["25%"]
    height = y_to_data(ax, 0.05)

    # Box
    ax.add_artist(
        Rectangle(
            (_d["25%"], offset * height),
            width=_d["75%"] - _d["25%"],
            height=height,
            facecolor=color,
            linewidth=1.5,
            alpha=0.7,
        ),
    )

    # Bars
    ax.add_artist(
        Line2D(
            xdata=[data.median()],
            ydata=[offset * height, offset * height + height],
            color="white",
        ),
    )

    # Whiskers
    ax.add_artist(
        Line2D(
            xdata=[max(_d["25%"] - 1.5 * iqr, ax.get_xlim()[0]), _d["25%"]],
            ydata=[offset * height + height / 2],
            color=color,
            alpha=0.7,
        ),
    )
    ax.add_artist(
        Line2D(
            xdata=[_d["75%"], _d["75%"] + 1.5 * iqr],
            ydata=[offset * height + height / 2],
            color=color,
            alpha=0.7,
        ),
    )


def plot_parameter_distribution(
    kms: pd.Series,
    title: str,
    max_kms_to_plot: int = 20,
) -> tuple[Figure, Axes]:
    xmin = kms.min() * 0.8
    xmax = kms.max() * 1.2

    x = np.geomspace(xmin, xmax, 1001)
    y1 = gaussian_kde(kms)(x)

    with plt.rc_context(
        {
            "grid.color": "0.8",
            "xtick.color": "0.8",
            "ytick.color": "0.8",
            "xtick.labelcolor": "0.3",
            "ytick.labelcolor": "0.3",
        },
    ):
        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        ax.set_xlim(xmin, xmax)
        ax.set_xscale("log")

        ax.fill_between(x, y1, alpha=0.2)
        ax.plot(x, y1, label=f"Brenda, n={len(kms)}")
        ax.grid(visible=True)
        ax.set_frame_on(False)
        ax.legend()

    ax.set_title(title)

    if len(kms) < max_kms_to_plot:
        for val in kms.to_numpy():
            ax.axvline(val, ymin=0.045, ymax=0.065, color="black")
    return fig, ax


def plot_parameter_distributions(
    all_kms: pd.Series,
    organism_kms: pd.Series,
    *,
    organism_name: str,
) -> tuple[Figure, Axes]:
    x = np.geomspace(all_kms.min(), all_kms.max(), 1001)
    y1 = normalise(gaussian_kde(all_kms)(x))
    y2 = normalise(gaussian_kde(organism_kms)(x))

    with plt.rc_context(
        {
            "grid.color": "0.8",
            "xtick.color": "0.8",
            "ytick.color": "0.8",
            "xtick.labelcolor": "0.3",
            "ytick.labelcolor": "0.3",
        },
    ):
        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        ax.set_xlim(all_kms.min(), all_kms.max())
        ax.set_ylim(0, max(y1.max(), y2.max()) * 1.1)
        ax.set_xscale("log")

        ax.fill_between(x, y1, alpha=0.2)
        ax.fill_between(x, y2, alpha=0.2)
        ax.plot(x, y1, label="All")
        ax.plot(x, y2, label=organism_name)
        ax.legend()
        add_boxplot(ax, all_kms, "C0")
        add_boxplot(ax, organism_kms, "C1", offset=1)
        ax.grid()
        ax.set_frame_on(False)
    return fig, ax


def savefig(
    plot: Figure | Axes,
    filename: str,
    *,
    path: Path = Path("img"),
    file_format: str = "png",
    transparent: bool = False,
    dpi: float = 200,
) -> Path:
    path.mkdir(exist_ok=True, parents=True)

    fig = plot if isinstance(plot, Figure) else cast(Figure, unwrap(plot.get_figure()))

    filepath = path / f"{filename}.{file_format}"

    fig.savefig(
        filepath,
        bbox_inches="tight",
        transparent=transparent,
        dpi=dpi,
    )
    return filepath
