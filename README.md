SUPPORT, SCREENING, AND NEGATIVE GROWTH OF REFLECTED EXPONENTIAL FORMS

R. Arun Chandru

Version 1 -- 15 September 2026


ABSTRACT

We study compactly supported negative tests for exponential forms associated with reflected divisors in a vertical strip. For a fixed polynomial counting budget, we determine the order of the worst support required to attain a prescribed normalized negative margin in the presence of an off-axis pair. The estimate is uniform over arbitrary additional reflected pairs and infinite backgrounds, without separation between distinct locations. A centered conjugation symmetry changes the exponent through the parity of the local counting budget. We also derive an explicit small-displacement transition for finite screens and prove its stability under a fixed polynomial-count axis background. For a fixed divisor, negative values have a lower exponential growth rate determined by the outer displacement; a weighted local condition gives the matching upper rate. Finally, we construct locally semibounded forms with fixed sparse and logarithmic counting bounds whose negative envelopes dominate any prescribed growth. These results concerning abstract reflected forms separate support, normalized margin, and large-window growth.

CONTENTS

The nine .tex files constitute the complete LaTeX source. Compile
manuscript.tex; its eight input files must be in the same directory.
The bibliography is in references.tex.

build.py is an optional, standard-library-only Python build helper.
It checks source/reference mechanics and runs a TeX compiler.

BUILDING

Use a reasonably current TeX distribution with the standard packages
listed in manuscript.tex. With pdfLaTeX:

    pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape manuscript.tex

Repeat until references and contents are stable (normally three runs).

Alternatively, with Python 3.10+ and pdflatex on PATH:

    python build.py

With Tectonic:

    python build.py --engine tectonic

The Tectonic helper uses cached packages by default. On a machine
without the required cached TeX packages, either install/use a full
TeX distribution or explicitly permit the package downloads:

    python build.py --engine tectonic --allow-package-downloads

You may pass an absolute compiler path with --engine. The generated
PDF is build/manuscript.pdf. Source checks without compilation:

    python build.py --check-only

This release was compiled with Tectonic. Different TeX engines or
package versions may change line breaks or PDF metadata.
