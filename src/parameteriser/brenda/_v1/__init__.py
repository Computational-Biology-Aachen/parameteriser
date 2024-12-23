from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, TypeVar

import pandas as pd
from parameteriser._paths import _default_cache_dir
from zeep import Client

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


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
