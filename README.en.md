# Basketball Score Clipper

**English** · [简体中文](README.md)

[![Tests](https://github.com/leesandao/basketball-score-clipper/actions/workflows/test.yml/badge.svg)](https://github.com/leesandao/basketball-score-clipper/actions/workflows/test.yml)
[![Version](https://img.shields.io/github/v/release/leesandao/basketball-score-clipper)](https://github.com/leesandao/basketball-score-clipper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A local basketball video skill for Codex. **Version 0.2.0 finds when the ball enters the hoop and produces a timestamp table plus SRT subtitle markers for manual editing in Jianying/CapCut.** The invocation remains `$basketball-score-clipper`.

No dedicated GPU is required. By default, work directly from local or mounted NAS originals without rendering proxies or highlights. Video clipping is available only when explicitly requested.

## How it works

Inspect video metadata and duration → verify the hoop region → find candidates on CPU → review nearby consecutive frames → locate entry times → export Markdown and SRT.

**A detected candidate is not a confirmed basket.** The bundled detector uses color, motion and trajectory rules, not a trained model. False positives, occlusions and missed baskets remain possible. The agent using the skill or a person performs visual review; the Python scripts do not automate that judgment. No full-match precision or recall benchmark is claimed.

## Outputs

| File | Purpose |
| --- | --- |
| `reviewed-events.json` | Original-source times, evidence, review states and basket entry times |
| `basket-timestamps.md` | Chronological table with timecodes, seconds and timing qualifications |
| `basket-markers.srt` | An auxiliary subtitle track; each block starts at the basket entry time |

SRT provides **subtitle-based location markers, not native flag markers**. Blocks last one second by default. Unconfirmed candidates are excluded. Place the original video at timeline zero at its original speed; trimmed, concatenated or retimed timelines require an explicit time mapping. Generated table headings and SRT labels currently use Chinese; both user guides explain them.

## Suitable footage

| Scenario | Suitability |
| --- | --- |
| Fixed camera, one stationary hoop, clearly visible orange ball | Suitable for the CPU baseline; review is still required |
| Known timestamps or already reviewed event JSON | Export immediately without rescanning the video |
| Local or mounted NAS long-form footage | Read directly; decoding, network and candidate volume affect runtime |
| Handheld, panning, zooming or multiple hoops | Revalidate ROI per stable section, review manually or supply a trained detector |
| Tiny ball, backlighting, blur or heavy occlusion | Not suitable for unattended confirmation |

See [use cases and limitations](docs/use-cases.en.md).

## Install and invoke

Use Python 3.11+. The full workflow needs FFmpeg/FFprobe; CPU detection additionally requires OpenCV and NumPy. Exporting an existing event JSON to Markdown/SRT uses only the Python standard library.

```bash
git clone https://github.com/leesandao/basketball-score-clipper.git "$HOME/.codex/skills/basketball-score-clipper"
cd "$HOME/.codex/skills/basketball-score-clipper"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-detect.txt
```

See the [English guide](docs/usage.en.md) for FFmpeg installation, virtual-environment discovery and preflight. Invoke in a new turn after installation; if not discovered, provide the absolute path to this repository's `SKILL.md`.

```text
Use $basketball-score-clipper to analyze /path/to/game.mp4.
Output only a made-basket timestamp table and an SRT marker file for Jianying.
Use the original video timeline and review the instant the ball enters the hoop.
List uncertain candidates separately. Do not cut or render video.
```

Try the exporter with synthetic data, without a video:

```bash
python scripts/export_timestamps.py \
  --events examples/reviewed-events.json \
  --output /tmp/basket-timestamps.md \
  --srt /tmp/basket-markers.srt --duration 120
```

Output paths must not already exist. Replace `--duration` with the actual source duration for your own data.

## Import into Jianying

Validated with Jianying Professional 11.4.2 on macOS: **字幕 (Captions) → 新建字幕 (New captions) → 导入本地字幕 (Import local subtitles) → select SRT → use the add button on the subtitle asset**. Confirm that the first block matches the table's time. Hide or remove the helper subtitle track before rendering your manually edited video. CapCut menu names may differ; this release does not claim a separate CapCut UI test.

## Documentation

- [English guide](docs/usage.en.md) / [中文使用指南](docs/usage.zh-CN.md)
- [Use cases](docs/use-cases.en.md) / [适用场景](docs/use-cases.zh-CN.md)
- [Bilingual changelog](CHANGELOG.md)
- [Event schema](references/event-schema.md) · [Detection modes](references/detection-modes.md)
- [Optional clipping workflow](references/clipping-workflow.md) · [Bilingual contributing guide](CONTRIBUTING.md)

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

Media integration tests require FFmpeg/FFprobe and detector tests require OpenCV; they skip when dependencies are absent. CI installs those dependencies and runs the full suite. Do not commit source footage, real match outputs or a machine-specific `runtime.json`.

Licensed under [MIT](LICENSE).
