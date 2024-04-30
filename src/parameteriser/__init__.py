from __future__ import annotations

from functools import partial
from typing import TypedDict, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import qtbutils as qu

from ._brenda import Brenda
from ._plot import plot_distributions
from ._tex import export_tex_document


class Describe(TypedDict):
    count: int
    mean: float
    std: float


def describe(s: pd.Series) -> Describe:
    return {
        "count": len(s),
        "mean": s.mean(),
        "std": s.std(),
    }


def routine(
    organism: str,
    ec: str,
    substrate: str,
    lower_percentile: int = 5,
    upper_percentile: int = 95,
) -> None:
    with open(".env") as fp:
        cred: dict[str, str] = dict(
            line.split("=", maxsplit=1) for line in fp.read().strip().split("\n")
        )

    TexPath = qu.default_path("tex")

    brenda = Brenda(email=cred["EMAIL"], password=cred["PASSWORD"])
    df = brenda.get_km(ec_number=ec)

    tex: list[str] = []
    all_kms = df["value"]
    organism_kms = df[df["organism"] == organism]["value"]

    all_kms_filtered = all_kms[
        all_kms.between(
            cast(float, np.percentile(all_kms, lower_percentile)),
            cast(float, np.percentile(all_kms, upper_percentile)),
        )
    ]
    organism_kms_filtered = organism_kms[
        organism_kms.between(
            cast(float, np.percentile(organism_kms, lower_percentile)),
            cast(float, np.percentile(organism_kms, upper_percentile)),
        )
    ]

    print(
        stats := pd.DataFrame(
            {
                "All": describe(all_kms),
                "All (filtered)": describe(all_kms_filtered),
                f"{organism}": describe(organism_kms),
                f"{organism} (filtered)": describe(organism_kms_filtered),
            }
        ).T
    )

    tex.append(
        stats.to_latex(
            formatters={
                "count": int,
                "mean": partial(np.format_float_scientific, precision=1, trim="0"),
                "std": partial(np.format_float_scientific, precision=1, trim="0"),
            }
        )
    )

    fig, ax = plot_distributions(
        all_kms,
        organism_kms,
        ec=ec,
        substrate=substrate,
        organism_name=organism,
    )
    path = qu.savefig(fig, f"km-{ec}-before-filtering", path=TexPath / "img")
    tex.append(
        qu.tex.figure(
            path.relative_to(*path.parts[:1]),
            caption="Distribution of Km values before any filtering was applied.",
            label=f"fig:km-{ec}-before",
            width=r"0.6\linewidth",
        )
    )
    plt.show()

    fig, ax = plot_distributions(
        all_kms_filtered,
        organism_kms_filtered,
        ec=ec,
        substrate=substrate,
        organism_name=organism,
    )
    path = qu.savefig(fig, f"km-{ec}-after-filtering", path=TexPath / "img")
    tex.append(
        qu.tex.figure(
            path.relative_to(*path.parts[:1]),
            caption=(
                f"Distribution of Km values after filtering out all values below "
                rf"{lower_percentile} \% or above {upper_percentile} \% percentile."
            ),
            label=f"fig:km-{ec}-after",
            width=r"0.6\linewidth",
        )
    )
    plt.show()

    with open(TexPath / "main.tex", "w") as fp:
        fp.write(export_tex_document("\n".join(tex), ""))


if __name__ == "__main__":
    routine(
        organism="Nicotiana tabacum",
        ec="4.1.1.39",
        substrate="CO2",
    )
