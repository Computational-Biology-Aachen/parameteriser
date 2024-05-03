from __future__ import annotations

import re
from dataclasses import dataclass, field
from logging import getLogger
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

RE_EC = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

logger = getLogger("parameteriser")


def _get_table_from_soup(soup: BeautifulSoup, id_: str) -> pd.DataFrame:
    table = soup.find("div", attrs={"id": id_})
    assert isinstance(table, Tag)

    headers = [i.text.strip() for i in table.find_all("div", attrs={"class": "header"})]
    cells = [i.text.strip() for i in table.find_all("div", attrs={"class": "cell"})]
    df = pd.DataFrame(data=np.array(cells).reshape(-1, len(headers)), columns=headers)
    df = df.drop(columns=["IMAGE"], errors="ignore")
    df.columns = df.columns.str.lower()
    return df.rename(
        columns={"km value [mm]": "value", "turnover number [1/s]": "value"},
    )


def _filter_uniprot_ids(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df["uniprot"] != "-") & (df["uniprot"] != "")]
    return df[
        df["uniprot"].str.fullmatch(
            r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",
        )
    ]


def _filter_and_convert_numeric_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[~df["value"].str.contains("-")]
    df.loc[:, "value"] = df["value"].astype(float)
    return df


def _filter_mutant_and_recombinant(df: pd.DataFrame) -> pd.DataFrame:
    s = df["commentary"].str
    return df.loc[~s.contains("mutant") ^ s.contains("recombin")]


def _get_uniprot_sequences(ids: Iterable[str]) -> pd.Series:
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
            soup = BeautifulSoup(wd.page_source)

        return _get_table_from_soup(soup, "tab12"), _get_table_from_soup(soup, "tab44")

    def get_kms_and_kcats(
        self,
        ec: str,
        *,
        check_ec: bool = True,
        filter_mutant: bool = True,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        if check_ec and RE_EC.fullmatch(ec) is None:
            msg = "ec %s doesn't follow expected format"
            raise ValueError(msg, ec)

        km_file = self._cache_dir / f"{ec}-km.json"
        kcat_file = self._cache_dir / f"{ec}-kcat.json"
        if km_file.exists() and kcat_file.exists():
            return pd.read_json(km_file), pd.read_json(kcat_file)

        kms, kcats = self._crawl_brenda_page(ec)

        kms = _filter_uniprot_ids(kms)
        kms = _filter_and_convert_numeric_values(kms)
        if filter_mutant:
            kms = _filter_mutant_and_recombinant(kms)

        kcats = _filter_uniprot_ids(kcats)
        kcats = _filter_and_convert_numeric_values(kcats)
        if filter_mutant:
            kcats = _filter_mutant_and_recombinant(kcats)

        uniprot_ids = set(kms["uniprot"].unique()).union(kcats["uniprot"].unique())
        logger.info("Found %s unique uniprot ids", len(uniprot_ids))

        sequences = _get_uniprot_sequences(uniprot_ids)
        logger.info("Found %s unique uniprot sequences", len(uniprot_ids))

        kms["sequence"] = [sequences[i] for i in kms["uniprot"]]
        kcats["sequence"] = [sequences[i] for i in kcats["uniprot"]]

        kms = kms.reset_index(drop=True)
        kcats = kcats.reset_index(drop=True)

        # Aggressive caching
        kms.to_json(km_file)
        kcats.to_json(kcat_file)

        return kms, kcats
