#!/usr/bin/env python3
"""Create a non-destructive basketball-score-clipper project layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CONFIG = {
    "version": 1,
    "directories": {
        "input": "input",
        "events": "events",
        "clips": "clips",
        "review": "review",
        "models": "models",
    },
    "detection": {
        "mode": "fixed-camera-baseline",
        "hoop_roi": None,
        "review_min_confidence": 0.55,
        "auto_accept_confidence": 0.85,
    },
    "clipping": {
        "release_pre_roll": 1.5,
        "fallback_lead": 4.0,
        "post_roll": 1.5,
        "encoder": "auto",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="project directory")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for directory in DEFAULT_CONFIG["directories"].values():
        (root / directory).mkdir(exist_ok=True)

    config_path = root / "basketball-score-clipper.json"
    if config_path.exists():
        print(f"Kept existing config: {config_path}")
    else:
        config_path.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"Created config: {config_path}")
    print(f"Project root: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
