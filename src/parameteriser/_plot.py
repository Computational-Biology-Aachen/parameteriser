from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from scipy.stats import gaussian_kde
from sspipe import p

from parameteriser._utils import unwrap

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
    pars: pd.Series,
    ax: Axes | None = None,
    color: str = "C0",
    xlim: tuple[float | None, float | None] | None = None,
) -> tuple[Figure, Axes]:
    x = np.geomspace(pars.min(), pars.max(), 1001)
    y = gaussian_kde(pars)(x)

    with plt.rc_context(
        {
            "grid.color": "0.8",
            "xtick.color": "0.8",
            "ytick.color": "0.8",
            "xtick.labelcolor": "0.3",
            "ytick.labelcolor": "0.3",
        },
    ):
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        else:
            fig = cast(Figure, ax.get_figure())

        if xlim is None:
            ax.set_xlim(pars.min(), pars.max())
        ax.set_ylim(0, y.max() * 1.1)
        ax.set_xscale("log")
        ax.fill_between(x, y, alpha=0.2, color=color)
        ax.plot(x, y, color=color)
        add_boxplot(ax, pars, color)
        ax.grid()
        ax.set_frame_on(False)
    return fig, ax


def plot_parameter_distributions(
    all_kms: pd.Series,
    organism_kms: pd.Series,
    *,
    organism_name: str,
) -> tuple[Figure, Axes]:
    x = np.geomspace(all_kms.min(), all_kms.max(), 1001)
    y1 = gaussian_kde(all_kms)(x) | p(normalise)
    y2 = gaussian_kde(organism_kms)(x) | p(normalise)

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


def savefig(  # noqa: PLR0913
    plot: Figure | Axes,
    filename: str,
    *,
    path: Path = Path("img"),
    file_format: str = "png",
    transparent: bool = False,
    dpi: float = 200,
) -> Path:
    path.mkdir(exist_ok=True, parents=True)

    fig = plot if isinstance(plot, Figure) else unwrap(plot.get_figure())

    filepath = path / f"{filename}.{file_format}"

    fig.savefig(
        filepath,
        bbox_inches="tight",
        transparent=transparent,
        dpi=dpi,
    )
    return filepath
