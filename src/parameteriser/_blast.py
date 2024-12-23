from __future__ import annotations

import io
import subprocess
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from parameteriser._paths import _default_temp_dir

__all__ = ["blast_sequence_against_others"]

if TYPE_CHECKING:
    from pathlib import Path


def _write_proteome(sequences: pd.Series, tmp_dir: Path) -> Path:
    proteome = tmp_dir / "proteome.fasta"

    with proteome.open("w") as fp:
        for idx, seq in sequences.items():
            wrapped = "\n".join(textwrap.wrap(seq, width=79))
            fp.write(f">{idx}\n{wrapped}\n")
    return proteome


def _generate_pblast_db(proteome: Path) -> Path:
    proteome_db = proteome.parent / proteome.stem
    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "makeblastdb",
            "-in",
            proteome,
            "-parse_seqids",
            "-blastdb_version",
            "5",
            "-dbtype",
            "prot",
            "-out",
            proteome_db,
        ],
        capture_output=True,
        check=True,
    )
    return proteome_db


def _write_query_file(query: str, tmp_dir: Path) -> Path:
    query_file = tmp_dir / "query.fasta"
    with query_file.open("w") as fp:
        seq = "\n".join(textwrap.wrap(query, width=79))
        fp.write(f">query\n{seq}\n")
    return query_file


def _run_blastp(
    query: Path,
    db: Path,
) -> pd.DataFrame:
    """Search protein database using a protein query

    Attributes
    ----------
    query_file_path: str or Path
        Path of the query file

    Returns
    -------
    matches: str
        Outputs the matches in a tsv table format as a multiline-string

    """
    out = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "blastp",
            "-db",
            db,
            "-query",
            query,
            "-outfmt",
            "6 qseqid sseqid evalue pident qcovs",
        ],
        capture_output=True,
        check=True,
    )
    if out.returncode != 0:
        msg = f"Process failed: {out.stderr.decode('utf-8')}"
        raise ValueError(msg)

    df = (
        pd.read_csv(
            io.StringIO(out.stdout.decode("utf-8")),
            sep="\t",
            header=None,
            names=["Monomer", "qseqid", "evalue", "pident", "qcovs"],
        )
        .sort_values(by=["pident"], ascending=False)
        .set_index("qseqid", drop=True)
    )
    df = df[~df.index.duplicated(keep="first")]
    df = df.drop(columns=["Monomer"])
    df.index.name = None
    return df


def blast_sequence_against_others(
    query: str,
    others: pd.Series,
    tmp_dir: Path | None = None,
) -> pd.DataFrame:
    tmp_dir = _default_temp_dir() if tmp_dir is None else tmp_dir

    return _run_blastp(
        query=_write_query_file(query, tmp_dir),
        db=_generate_pblast_db(_write_proteome(sequences=others, tmp_dir=tmp_dir)),
    )
