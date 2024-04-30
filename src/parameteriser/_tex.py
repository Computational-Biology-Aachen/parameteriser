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
