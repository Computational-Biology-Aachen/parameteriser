from __future__ import annotations

from typing import TYPE_CHECKING

__all__ = [
    "bold",
    "chapter",
    "clearpage",
    "export_tex_document",
    "figure",
    "list_as_bold",
    "list_with_headers",
    "math",
    "math_il",
    "mathrm",
    "paragraph",
    "part",
    "section",
    "section_",
    "subparagraph",
    "subsection",
    "subsection_",
    "subsubsection",
    "subsubsection_",
]

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

right_arrow = r"\xrightarrow{}"
newline = r"\\" + "\n"
floatbarrier = r"\FloatBarrier"


def part(s: str) -> str:
    return floatbarrier + rf"\part{{{s}}}"


def chapter(s: str) -> str:
    return floatbarrier + rf"\part{{{s}}}"


def section(s: str) -> str:
    return floatbarrier + rf"\section{{{s}}}"


def section_(s: str) -> str:
    return floatbarrier + rf"\section*{{{s}}}"


def subsection(s: str) -> str:
    return floatbarrier + rf"\subsection{{{s}}}"


def subsection_(s: str) -> str:
    return floatbarrier + rf"\subsection*{{{s}}}"


def subsubsection(s: str) -> str:
    return floatbarrier + rf"\subsubsection{{{s}}}"


def subsubsection_(s: str) -> str:
    return floatbarrier + rf"\subsubsection*{{{s}}}"


def paragraph(s: str) -> str:
    return rf"\paragraph{{{s}}}"


def subparagraph(s: str) -> str:
    return rf"\subparagraph{{{s}}}"


def math_il(s: str) -> str:
    return f"${s}$"


def math(s: str) -> str:
    return f"$${s}$$"


def mathrm(s: str) -> str:
    return rf"\mathrm{{{s}}}"


def bold(s: str) -> str:
    return rf"\textbf{{{s}}}"


def clearpage() -> str:
    return r"\clearpage"


def list_with_headers(
    rows: list[tuple[str, str]],
    sec_fn: Callable[[str], str],
) -> str:
    return "\n\n".join(
        [
            "\n".join(
                (
                    sec_fn(name),
                    content,
                ),
            )
            for name, content in rows
        ],
    )


def list_as_bold(rows: list[tuple[str, str]]) -> str:
    return "\n\n".join(
        [
            "\n".join(
                (
                    bold(name) + r"\\",
                    content,
                    r"\vspace{20pt}",
                ),
            )
            for name, content in rows
        ],
    )


def figure(
    path: Path,
    caption: str,
    label: str,
    width: str = r"\linewidth",
) -> str:
    return rf"""\begin{{figure}}
  \centering
  \includegraphics[width={width}]{{{path.as_posix()}}}
  \caption{{{caption}}}
  \label{{{label}}}
\end{{figure}}
"""


def export_tex_document(
    content: str,
    author: str,
    title: str = "Model construction",
) -> str:
    return rf"""\documentclass{{article}}
\usepackage[english]{{babel}}
\usepackage[a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm,marginparwidth=1.75cm]{{geometry}}
\usepackage{{amsmath, amssymb, array, booktabs, breqn, caption, longtable, mathtools, ragged2e, tabularx, titlesec, titling}}
\newcommand{{\sectionbreak}}{{\clearpage}}
\setlength{{\parindent}}{{0pt}}
\title{{{title}}}
\date{{}} % clear date
\author{{{author}}}
\begin{{document}}
\maketitle
\tableofcontents

{content}
\end{{document}}
"""
