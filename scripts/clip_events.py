#!/usr/bin/env python3
"""Create frame-accurate MP4 clips from basketball score event JSON."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def probe_media(ffprobe: str, source: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,pix_fmt,color_transfer,color_primaries,color_space",
            "-of",
            "json",
            str(source),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {source}: {proc.stderr.strip()}")
    payload = json.loads(proc.stdout)
    try:
        duration = float(payload.get("format", {}).get("duration"))
    except (TypeError, ValueError) as exc:
        raise ValueError("source duration must be numeric") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("source duration must be a positive finite number")
    video = next(
        (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
        {},
    )
    transfer = str(video.get("color_transfer") or "").lower()
    hdr = transfer in {"smpte2084", "arib-std-b67"}
    return {"duration": duration, "hdr": hdr, "video": video}


def list_encoders(ffmpeg: str) -> set[str]:
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-encoders"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    text = proc.stdout + proc.stderr
    return {name for name in ("h264_nvenc", "h264_videotoolbox", "libx264") if name in text}


def choose_encoder(requested: str, encoders: set[str]) -> str:
    if requested != "auto":
        if requested != "copy" and requested not in encoders:
            raise RuntimeError(f"requested encoder is unavailable: {requested}")
        return requested
    for encoder in ("h264_nvenc", "h264_videotoolbox", "libx264"):
        if encoder in encoders:
            return encoder
    raise RuntimeError("no supported H.264 encoder found")


def encoder_args(encoder: str) -> list[str]:
    if encoder == "copy":
        return ["-c", "copy"]
    if encoder == "h264_nvenc":
        return [
            "-c:v",
            encoder,
            "-preset",
            "p5",
            "-cq",
            "20",
            "-b:v",
            "0",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
        ]
    if encoder == "h264_videotoolbox":
        return ["-c:v", encoder, "-q:v", "65", "-c:a", "aac", "-b:a", "192k"]
    return [
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
    ]


def sanitize(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return cleaned or "event"


def resolve_source(raw: str, source_root: Path | None, events_path: Path) -> Path:
    source = Path(raw).expanduser()
    if not source.is_absolute():
        source = (source_root or events_path.parent) / source
    return source.resolve()


def event_bounds(event: dict[str, Any], args: argparse.Namespace) -> tuple[float, float]:
    score = finite_number(event.get("score_time"), "score_time")
    if event.get("clip_start") is not None and event.get("clip_end") is not None:
        start = finite_number(event["clip_start"], "clip_start")
        end = finite_number(event["clip_end"], "clip_end")
    elif event.get("release_time") is not None:
        start = finite_number(event["release_time"], "release_time") - args.pre_roll
        end = score + args.post_roll
    elif event.get("candidate_start") is not None:
        start = finite_number(event["candidate_start"], "candidate_start")
        end = score + args.post_roll
    else:
        start = score - args.fallback_lead
        end = score + args.post_roll
    return max(0.0, start), end


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--min-confidence", type=float)
    parser.add_argument("--include-candidates", action="store_true")
    parser.add_argument("--pre-roll", type=float, default=1.5)
    parser.add_argument("--fallback-lead", type=float, default=4.0)
    parser.add_argument("--post-roll", type=float, default=1.5)
    parser.add_argument(
        "--encoder",
        choices=("auto", "h264_nvenc", "h264_videotoolbox", "libx264", "copy"),
        default="auto",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    if args.min_confidence is None:
        args.min_confidence = 0.55 if args.include_candidates else 0.85
    if not 0 <= args.min_confidence <= 1:
        parser.error("--min-confidence must be between 0 and 1")
    for name in ("pre_roll", "fallback_lead", "post_roll"):
        if getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} must be non-negative")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        print("ffmpeg and ffprobe are required", file=sys.stderr)
        return 2

    events_path = args.events.expanduser().resolve()
    document = json.loads(events_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("events"), list):
        raise ValueError("event file must be an object containing an events array")

    encoder = choose_encoder(args.encoder, list_encoders(ffmpeg))
    allowed_results = {"made"}
    if args.include_candidates:
        allowed_results.add("made_candidate")

    selected: list[dict[str, Any]] = []
    for index, event in enumerate(document["events"], start=1):
        if not isinstance(event, dict):
            raise ValueError(f"event {index} must be an object")
        if event.get("result") not in allowed_results:
            continue
        confidence = finite_number(event.get("confidence"), "confidence")
        if not 0 <= confidence <= 1:
            raise ValueError(f"event {index} confidence must be between 0 and 1")
        if confidence < args.min_confidence and not (
            args.include_candidates and event.get("result") == "made_candidate"
        ):
            continue
        source_raw = event.get("source") or document.get("source")
        if not isinstance(source_raw, str) or not source_raw:
            raise ValueError(f"event {index} has no source")
        selected.append({"index": index, "event": event, "source_raw": source_raw})

    if not selected:
        print(json.dumps({"status": "done", "clips": [], "notes": "no events selected"}))
        return 0

    args.output_dir = args.output_dir.expanduser().resolve()
    manifest_path = None
    if not args.dry_run:
        manifest_path = (args.manifest or (args.output_dir / "clips-manifest.json")).resolve()
        if manifest_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"manifest exists; pass --overwrite or choose --manifest: {manifest_path}"
            )
    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    media_cache: dict[Path, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    planned_outputs: set[Path] = set()
    for sequence, item in enumerate(selected, start=1):
        event = item["event"]
        source = resolve_source(item["source_raw"], args.source_root, events_path)
        if not source.is_file():
            raise FileNotFoundError(f"source video not found: {source}")
        if source not in media_cache:
            media_cache[source] = probe_media(ffprobe, source)
        media = media_cache[source]
        duration = media["duration"]
        if media["hdr"] and encoder != "copy":
            raise RuntimeError(
                f"HDR source requires an HDR-aware workflow or --encoder copy: {source}"
            )
        start, end = event_bounds(event, args)
        end = min(end, duration)
        if end <= start:
            raise ValueError(f"event {event.get('id', item['index'])} has invalid boundaries")

        event_id = sanitize(str(event.get("id") or f"score-{sequence:04d}"))
        timestamp = f"{event.get('score_time', 0):010.3f}".replace(".", "-")
        output = args.output_dir / f"{sanitize(source.stem)}_{event_id}_{timestamp}.mp4"
        if output in planned_outputs:
            raise ValueError(f"duplicate output path: {output}")
        planned_outputs.add(output)
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"output exists; pass --overwrite to replace it: {output}")

        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y" if args.overwrite else "-n",
            "-ss",
            f"{start:.6f}",
            "-i",
            str(source),
            "-t",
            f"{end - start:.6f}",
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-map_metadata",
            "0",
            *encoder_args(encoder),
        ]
        if encoder != "copy":
            command.extend(["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
        command.append(str(output))

        result = {
            "event_id": event_id,
            "source": str(source),
            "output": str(output),
            "start": round(start, 6),
            "end": round(end, 6),
            "duration": round(end - start, 6),
            "encoder": encoder,
            "command": command,
            "status": "planned" if args.dry_run else "pending",
        }
        if not args.dry_run:
            proc = subprocess.run(command, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                result["status"] = "failed"
                result["error"] = proc.stderr.strip()
                results.append(result)
                break
            result["status"] = "created"
        results.append(result)

    manifest = {
        "version": 1,
        "events_file": str(events_path),
        "encoder": encoder,
        "dry_run": args.dry_run,
        "clips": results,
    }
    if not args.dry_run:
        assert manifest_path is not None
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        manifest["manifest"] = str(manifest_path)

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 1 if any(item["status"] == "failed" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
