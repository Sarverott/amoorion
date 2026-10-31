"""Fail on what would stop the PDF of Read the Docs: `task docs:check:latex`.

pdflatex stops at the 100th character it doesn't know, leaving no PDF, so one
notebook output with unusual characters can break every build of the docs. These
are the ones known by default, and those docs/conf.py declares. For a new one:
declare it in `latex_elements` there.
"""

import re
import sys
from pathlib import Path

KNOWN = {
    *range(
        0xA0,
        0x180,
    ),
    *range(
        0x2013,
        0x2015,
    ),
    *range(
        0x2018,
        0x201F,
    ),
    0x2022,
    0x2026,
}


def unknown(tex: str) -> set[str]:
    """Characters of the LaTeX source that pdflatex would refuse."""

    declared = {
        int(code, 16)
        for code in re.findall(r"\\DeclareUnicodeCharacter\{([0-9A-F]+)\}", tex)
    }

    return {
        char
        for char in tex
        if ord(char) > 127 and ord(char) not in KNOWN | declared
    }


if __name__ == "__main__":
    text = Path(sys.argv[1]).read_text()

    found = unknown(text)

    if found:
        sys.exit(
            "pdflatex won't know: "
            + " ".join(sorted(f"{char} (U+{ord(char):04X})" for char in found))
        )

    # An SVG image is an error of LaTeX as well: see _no_badges_on_paper in docs/_ext.
    if re.search(r"\\sphinxincludegraphics[^\n]*\.svg", text):
        sys.exit("an SVG image is in the LaTeX source: LaTeX can't embed it")
