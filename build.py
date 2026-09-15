#!/usr/bin/env python3
"""Build the P4 paper and check source/reference mechanics, not its proofs.

Requires Python 3.10+ and a separately installed pdflatex or Tectonic.
No third-party Python packages are required. Shell escape is never enabled.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys


SOURCES = (
    "manuscript.tex",
    "introduction.tex",
    "basics.tex",
    "frontier.tex",
    "screening.tex",
    "growth.tex",
    "arbitrary_growth.tex",
    "arithmetic.tex",
    "references.tex",
)


def check_sources(root: Path) -> None:
    texts = {}
    for name in SOURCES:
        path = root / name
        if not path.is_file():
            raise ValueError(f"Missing source: {name}")
        text = path.read_text(encoding="utf-8-sig")
        if "\ufffd" in text:
            raise ValueError(f"Replacement character in {name}")
        if any(ord(ch) < 32 and ch not in "\r\n\t" for ch in text):
            raise ValueError(f"Unexpected control character in {name}")
        texts[name] = text

    inputs = re.findall(r"\\input\{([^}]+)\}", texts["manuscript.tex"])
    if set(inputs) != set(SOURCES[1:]) or len(inputs) != len(SOURCES) - 1:
        raise ValueError("Master inputs differ from the declared source set")
    labels = []
    references = []
    bibitems = []
    citations = []
    for name, text in texts.items():
        labels.extend(re.findall(r"\\label\{([^}]+)\}", text))
        references.extend(re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", text))
        bibitems.extend(re.findall(r"\\bibitem(?:\[[^]]*\])?\{([^}]+)\}", text))
        for group in re.findall(r"\\cite(?:\[[^]]*\])?\{([^}]+)\}", text):
            citations.extend(key.strip() for key in group.split(","))
        if re.search(r"(?<!\\)\bqquad\b", text):
            raise ValueError(f"Unescaped spacing command in {name}")
    if len(labels) != len(set(labels)):
        raise ValueError("Duplicate equation/section labels")
    if len(bibitems) != len(set(bibitems)):
        raise ValueError("Duplicate bibliography keys")
    missing_refs = set(references) - set(labels)
    missing_cites = set(citations) - set(bibitems)
    if missing_refs or missing_cites:
        raise ValueError(
            f"Unresolved labels: {sorted(missing_refs)}; "
            f"unresolved citations: {sorted(missing_cites)}"
        )
    print(f"Source mechanics: {len(SOURCES)} TeX files, "
          f"{len(labels)} unique labels, {len(bibitems)} bibliography entries.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", help="Path/name of pdflatex or tectonic")
    parser.add_argument("--outdir", default="build",
                        help="Build directory relative to this script")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--allow-package-downloads", action="store_true",
                        help="Permit Tectonic to fetch missing TeX packages")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    check_sources(root)
    if args.check_only:
        print("These checks are not a mathematical verification.")
        return 0

    engine = args.engine or shutil.which("pdflatex") or shutil.which("tectonic")
    if not engine:
        raise ValueError("Install a TeX distribution or supply --engine.")
    resolved = shutil.which(engine) or engine
    name = Path(resolved).stem.lower()
    if name not in {"pdflatex", "tectonic"}:
        raise ValueError("--engine must identify pdflatex or tectonic")

    output = (root / args.outdir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if name == "tectonic":
        command = [resolved, "--keep-logs", "--keep-intermediates",
                   "--outdir", str(output)]
        if not args.allow_package_downloads:
            command.append("--only-cached")
        command.append("manuscript.tex")
        subprocess.run(command, cwd=root, check=True)
    else:
        command = [resolved, "-interaction=nonstopmode", "-halt-on-error",
                   "-no-shell-escape", f"-output-directory={output}",
                   "manuscript.tex"]
        for _ in range(3):
            subprocess.run(command, cwd=root, check=True)

    log_path = output / "manuscript.log"
    if not log_path.is_file():
        raise ValueError("Compiler produced no log")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    problems = []
    for pattern, description in (
        (r"(?im)^! ", "TeX error"),
        (r"(?i)(?:Reference|Citation) .*? undefined", "undefined reference/citation"),
        (r"(?i)There were undefined references", "undefined references"),
        (r"(?i)Label\(s\) may have changed", "unstable cross-references"),
        (r"(?i)multiply defined", "multiply defined label"),
        (r"(?i)Overfull \\[hv]box", "overfull box"),
    ):
        if re.search(pattern, log):
            problems.append(description)
    pdf = output / "manuscript.pdf"
    if not pdf.is_file() or pdf.stat().st_size == 0:
        problems.append("missing PDF")
    if problems:
        raise ValueError("Inspect the build log: " + ", ".join(problems))
    print(f"Built {pdf}")
    print("Compilation and reference checks passed. "
          "They do not verify the mathematics or replace visual review.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Build/check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
