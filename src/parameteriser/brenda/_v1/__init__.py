from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, TypedDict, TypeVar, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from parameteriser import _tex
from parameteriser._paths import _default_cache_dir, _default_path
from parameteriser._plot import plot_parameter_distributions, savefig
from parameteriser._tex import export_tex_document
from zeep import Client


@dataclass
class BrendaType:
    ...


DataClass = TypeVar("DataClass", bound=BrendaType)


@dataclass
class Km(BrendaType):
    value: float
    substrate: str
    organism: str
    commentary: str | None
    literature: list[str]


@dataclass
class Sequence(BrendaType):
    first_accession_code: str
    naa: int
    sequence: str
    source: str
    organism: str
    id: str


@dataclass
class Brenda:
    email: str
    password: str
    tmp_dir: Path = field(default=_default_cache_dir())
    wsdl: str = "https://www.brenda-enzymes.org/soap/brenda_zeep.wsdl"

    def __post_init__(self) -> None:
        self.password = hashlib.sha256(self.password.encode("utf-8")).hexdigest()
        self.tmp_dir.mkdir(exist_ok=True, parents=True)

    def _cache_result(
        self,
        *,
        filename: Path,
        obj_type: type[DataClass],
        download_fn: Callable[..., list[DataClass]],
        verbose: bool = False,
    ) -> list[DataClass]:
        if filename.exists():
            if verbose:
                pass
            with filename.open(encoding="utf-8") as fp:
                data = [obj_type(**i) for i in json.load(fp)]
        else:
            if verbose:
                pass
            data = download_fn()
            with filename.open("w", encoding="utf-8") as fp:
                json.dump([asdict(i) for i in data], fp)

        return data

    def get_km(self, ec_number: str, *, verbose: bool = False) -> pd.DataFrame:
        def download() -> list[Km]:
            return [
                Km(
                    value=float(res["kmValue"]),
                    substrate=res["substrate"],
                    organism=res["organism"],
                    commentary=res["commentary"],
                    literature=res["literature"],
                )
                for res in Client(self.wsdl).service.getKmValue(
                    self.email,
                    self.password,
                    f"ecNumber*{ec_number}",
                    "organism*",
                    "kmValue*",
                    "kmValueMaximum*",
                    "substrate*",
                    "commentary*",
                    "ligandStructureId*",
                    "literature*",
                )
            ]

        return pd.DataFrame(
            self._cache_result(
                filename=self.tmp_dir / f"km-{ec_number}.json",
                obj_type=Km,
                download_fn=download,
                verbose=verbose,
            ),
        )

    def get_sequences(self, ec_number: str, *, verbose: bool = False) -> pd.DataFrame:
        def download() -> list[Sequence]:
            return [
                Sequence(
                    first_accession_code=i["firstAccessionCode"],
                    naa=int(i["noOfAminoAcids"]),
                    sequence=i["sequence"],
                    source=i["source"],
                    organism=i["organism"],
                    id=i["id"],
                )
                for i in Client(self.wsdl).service.getSequence(
                    self.email,
                    self.password,
                    f"ecNumber*{ec_number}",
                    "sequence*",
                    "noOfAminoAcids*",
                    "firstAccessionCode*",
                    "source*",
                    "id*",
                    "organism*",
                )
            ]

        return pd.DataFrame(
            self._cache_result(
                filename=self.tmp_dir / f"sequences-{ec_number}.json",
                obj_type=Sequence,
                download_fn=download,
                verbose=verbose,
            ),
        )


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
    with Path(".env").open() as fp:
        cred: dict[str, str] = dict(
            line.split("=", maxsplit=1) for line in fp.read().strip().split("\n")
        )

    TexPath = _default_path("tex")

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

    # tex.append(
    #     stats.to_latex(
    #         formatters={  # noqa: ERA001
    #             "count": int,  # noqa: ERA001
    #             "mean": partial(np.format_float_scientific, precision=1, trim="0"),  # noqa: ERA001
    #             "std": partial(np.format_float_scientific, precision=1, trim="0"),  # noqa: ERA001
    #         },
    #     ),
    # )  # noqa: ERA001

    fig, ax = plot_parameter_distributions(
        all_kms,
        organism_kms,
        ec=ec,
        substrate=substrate,
        organism_name=organism,
    )
    path = savefig(fig, f"km-{ec}-before-filtering", path=TexPath / "img")
    tex.append(
        _tex.figure(
            path.relative_to(*path.parts[:1]),
            caption="Distribution of Km values before any filtering was applied.",
            label=f"fig:km-{ec}-before",
            width=r"0.6\linewidth",
        ),
    )
    plt.show()

    fig, ax = plot_parameter_distributions(
        all_kms_filtered,
        organism_kms_filtered,
        ec=ec,
        substrate=substrate,
        organism_name=organism,
    )
    path = savefig(fig, f"km-{ec}-after-filtering", path=TexPath / "img")
    tex.append(
        _tex.figure(
            path.relative_to(*path.parts[:1]),
            caption=(
                f"Distribution of Km values after filtering out all values below "
                rf"{lower_percentile} \% or above {upper_percentile} \% percentile."
            ),
            label=f"fig:km-{ec}-after",
            width=r"0.6\linewidth",
        ),
    )
    plt.show()

    with (TexPath / "main.tex").open("w") as fp:
        fp.write(export_tex_document("\n".join(tex), ""))


if __name__ == "__main__":
    routine(
        organism="Nicotiana tabacum",
        ec="4.1.1.39",
        substrate="CO2",
    )
