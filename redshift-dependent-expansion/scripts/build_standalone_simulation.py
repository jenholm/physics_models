#!/usr/bin/env python3
"""Assemble a portable single-file copy of the public visualization.

Inlines styles.css, simulation.js and the frozen publication JSON into
simulation/dist/redshift_expansion_simulation.html so one file can be
shared or hosted anywhere. The checked-in development source stays split
and reviewable; this output is generated, not hand-edited.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SIM_DIR = REPO_ROOT / "simulation"
OUT_PATH = SIM_DIR / "dist" / "redshift_expansion_simulation.html"

P5_CDN = "https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"


def main():
    html = (SIM_DIR / "index.html").read_text()
    css = (SIM_DIR / "styles.css").read_text()
    js = (SIM_DIR / "simulation.js").read_text()
    payload = json.loads(
        (SIM_DIR / "data" / "publication_simulation_data.json").read_text()
    )

    for token in ("</style", "</script"):
        assert token not in css, f"inline blocker in css: {token}"
    assert "</script" not in js, "inline blocker in js"

    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        "<style>\n" + css + "\n</style>",
    )
    html = html.replace(
        '<script src="simulation.js"></script>',
        "<script>\nwindow.__RDE_DATA = "
        + json.dumps(payload, separators=(",", ":"))
        + ";\n</script>\n<script>\n"
        + js
        + "\n</script>",
    )
    assert P5_CDN in html, "p5 CDN reference must survive the build"
    assert "__RDE_DATA" in html

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
