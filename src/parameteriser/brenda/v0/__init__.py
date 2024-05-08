from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from parameteriser._paths import _default_cache_dir
from selenium import webdriver
from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from pathlib import Path

RE_EC: re.Pattern[str] = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
UNIPROT_PATTERN: str = (
    r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}"
)
RE_UNIPROT = re.compile(UNIPROT_PATTERN)

logger = getLogger("parameteriser")


@dataclass
class KineticParameterFromJson:
    value: float
    substrate: str
    organism: str
    uniprot: str
    commentary: str


def _get_table_from_soup(soup: BeautifulSoup, id_: str) -> pd.DataFrame:
    table = soup.find("div", attrs={"id": id_})
    assert isinstance(table, Tag)

    headers = [i.text.strip() for i in table.find_all("div", attrs={"class": "header"})]
    cells = [i.text.strip() for i in table.find_all("div", attrs={"class": "cell"})]
    df = pd.DataFrame(data=np.array(cells).reshape(-1, len(headers)), columns=headers)
    df = df.drop(columns=["IMAGE", "literature"], errors="ignore")
    df.columns = df.columns.str.lower()
    return df.rename(
        columns={"km value [mm]": "value", "turnover number [1/s]": "value"},
    )


def _filter_uniprot_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df["uniprot"] != "-") & (df["uniprot"] != "")]
    return df[df["uniprot"].str.fullmatch(UNIPROT_PATTERN)]


def _filter_and_convert_numeric_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[~df["value"].str.contains("-")]
    df.loc[:, "value"] = df["value"].astype(float)
    return df


def _download_uniprot_sequences(ids: Iterable[str]) -> pd.Series:
    from more_itertools import batched

    sequences = {}
    for batch in batched(ids, n=20):
        accessions = "+OR+accession:".join(batch)

        resp = requests.get(
            f"https://rest.uniprot.org/uniprotkb/search?query=accession:{accessions}&fields=sequence",
            timeout=10,
        )

        if not resp.ok:
            msg = "Connection failed or bad request"
            raise ValueError(msg)

        if (results := resp.json().get("results", None)) is None:
            msg = "Bad json"
            raise ValueError(msg)
        if len(results) == 0:
            msg = "No results"
            raise ValueError(msg)

        for result in results:
            sequences[result["primaryAccession"]] = result["sequence"]["value"]

    return pd.Series(sequences)


def _add_uniprot_sequences(kms: pd.DataFrame, kcats: pd.DataFrame) -> None:
    uniprot_ids = set(kms["uniprot"].unique()).union(kcats["uniprot"].unique())
    sequences = _download_uniprot_sequences(uniprot_ids)
    kms["sequence"] = [sequences[i] for i in kms["uniprot"]]
    kcats["sequence"] = [sequences[i] for i in kcats["uniprot"]]


def _mutant_annotation_to_boolean(df: pd.DataFrame) -> pd.DataFrame:
    df["is_mutant"] = df["commentary"].str.contains("mutant")
    df["is_recombinant"] = df["commentary"].str.contains("recombin")
    return df.drop(columns=["commentary"])


def _extract_uniprot_accessions_from_db(
    proteins: dict[str, list[dict[str, str | list[str]]]],
) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}

    for k, vs in proteins.items():
        _accs: set[str] = set()
        for v in vs:
            if isinstance(v, list):
                _accs.update([i for i in v if RE_UNIPROT.fullmatch(i)])
                continue
            if v.get("source", "") != "uniprot":
                continue
            if (accessions := v.get("accessions")) is None:
                continue
            _accs.update([i for i in accessions if RE_UNIPROT.fullmatch(i)])
        if len(_accs) > 0:
            res[k] = sorted(_accs)
    return res


def _extract_organism_from_db(organisms: dict[str, dict[str, str]]) -> dict[str, str]:
    return {
        k: value for k, v in organisms.items() if (value := v.get("value")) is not None
    }


def _read_kinetic_parameter_from_db(
    enzyme: dict,
    group: str,
    organisms: dict[str, str],
    uniprot: dict[str, list[str]],
) -> pd.DataFrame:
    pars = []
    for v in enzyme.get(group, {}):
        if (_value := v.get("num_value")) is None:
            continue
        if (_substrate := v.get("value")) is None:
            continue
        _comment = v.get("comment", "")

        for idx in v.get("proteins", []):
            if (accession := uniprot.get(idx)) is None:
                continue
            if (organism_name := organisms.get(idx)) is None:
                continue

            # FIXME: better way of deciding which accession to choose
            pars.append(
                KineticParameterFromJson(
                    value=_value,
                    substrate=_substrate,
                    organism=organism_name,
                    uniprot=accession[0],
                    commentary=_comment,
                ),
            )
    return pd.DataFrame(
        pars,
        columns=["value", "substrate", "organism", "uniprot", "commentary"],
    )


def _read_km_and_kcat_from_db(enzyme: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    organisms = _extract_organism_from_db(enzyme.get("organisms", {}))
    uniprot = _extract_uniprot_accessions_from_db(enzyme.get("proteins", {}))

    kms = _read_kinetic_parameter_from_db(
        enzyme=enzyme,
        group="km_value",
        organisms=organisms,
        uniprot=uniprot,
    )
    kcats = _read_kinetic_parameter_from_db(
        enzyme=enzyme,
        group="turnover_number",
        organisms=organisms,
        uniprot=uniprot,
    )

    return kms, kcats


def select_organism(df: pd.DataFrame, organism: str) -> pd.DataFrame:
    return df[df["organism"] == organism].drop(columns=["organism"])


def estimate_mean_std(values: pd.Series) -> tuple[float, float]:
    from math import sqrt

    from scipy.integrate import quad
    from scipy.stats import gaussian_kde

    kde = gaussian_kde(values)
    mean, _err = quad(lambda x: x * kde.pdf(x), -np.inf, np.inf)
    integral, _err = quad(lambda x: x**2 * kde.pdf(x), -np.inf, np.inf)
    var = integral - mean**2
    return mean, sqrt(var)


@dataclass
class Brenda:
    _brenda_url: str = "https://www.brenda-enzymes.org"
    _cache_dir: Path = field(default=_default_cache_dir())

    def __post_init__(self) -> None:
        self._cache_dir.mkdir(exist_ok=True, parents=True)

    def _crawl_brenda_page(self, ec: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")

        with webdriver.Chrome(options=options) as wd:
            wd.get(f"{self._brenda_url}/enzyme.php?ecno={ec}")

            wd.find_element(By.LINK_TEXT, "Functional Parameters").click()
            wd.find_element(By.LINK_TEXT, "KM Values").click()
            wd.find_element(By.LINK_TEXT, "Turnover Numbers").click()

            # Needs to be reversed, as apparently otherwise wrong elements are referenced
            # when stuff is appended to the DOM
            for el in reversed(
                wd.find_element(By.ID, "tab44").find_elements(
                    By.CLASS_NAME,
                    "rowpreview",
                ),
            ):
                el.click()
            for el in reversed(
                wd.find_element(By.ID, "tab12").find_elements(
                    By.CLASS_NAME,
                    "rowpreview",
                ),
            ):
                el.click()

            # Now source can be loaded
            soup = BeautifulSoup(wd.page_source, features="lxml")

        return _get_table_from_soup(soup, "tab12"), _get_table_from_soup(soup, "tab44")

    def _load_or_download(self, ec: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        km_file = self._cache_dir / f"{ec}-km.json"
        kcat_file = self._cache_dir / f"{ec}-kcat.json"

        # Load existing data if possible
        if km_file.exists() and kcat_file.exists():
            return pd.read_json(km_file), pd.read_json(kcat_file)

        # Otherwise download brenda data
        kms, kcats = self._crawl_brenda_page(ec)

        # Add uniprot sequence
        kms = _filter_uniprot_ids(kms)
        kcats = _filter_uniprot_ids(kcats)
        _add_uniprot_sequences(kms, kcats)

        # Convert numeric data
        kms = _filter_and_convert_numeric_values(kms)
        kcats = _filter_and_convert_numeric_values(kcats)

        # Convert mutant and recombinant annotation to boolean arrays
        kms = _mutant_annotation_to_boolean(kms)
        kcats = _mutant_annotation_to_boolean(kcats)

        # Reset index after filtering
        kms = kms.reset_index(drop=True)
        kcats = kcats.reset_index(drop=True)

        # Aggressive caching
        kms.to_json(km_file)
        kcats.to_json(kcat_file)
        return kms, kcats

    def read_database(self, db_json: Path) -> None:
        """Read in database in json format obtained from
        https://www.brenda-enzymes.org/download.php
        """
        with db_json.open() as fp:
            data: dict[str, dict] = json.load(fp)["data"]

        for ec, enzyme in data.items():
            # Add uniprot sequence
            kms, kcats = _read_km_and_kcat_from_db(enzyme)
            _add_uniprot_sequences(kms, kcats)

            # Convert mutant and recombinant annotation to boolean arrays
            kms = _mutant_annotation_to_boolean(kms)
            kcats = _mutant_annotation_to_boolean(kcats)

            kms.to_json(self._cache_dir / f"{ec}-km.json")
            kcats.to_json(self._cache_dir / f"{ec}-kcat.json")

    def get_kms_and_kcats(
        self,
        ec: str,
        organism: str | None = None,
        *,
        check_ec: bool = True,
        filter_mutant: bool = True,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if check_ec and RE_EC.fullmatch(ec) is None:
            msg = "ec %s doesn't follow expected format"
            raise ValueError(msg, ec)

        kms, kcats = self._load_or_download(ec=ec)

        if filter_mutant:
            kms = kms[~(kms["is_mutant"] ^ kms["is_recombinant"])]
            kcats = kcats[~(kcats["is_mutant"] ^ kcats["is_recombinant"])]

        if organism is not None:
            kms = select_organism(kms, organism)
            kcats = select_organism(kcats, organism)

        return kms, kcats
