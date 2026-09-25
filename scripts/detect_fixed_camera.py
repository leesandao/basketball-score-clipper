#!/usr/bin/env python3
"""Generate review-first made-basket candidates for stable, fixed-camera footage."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import deque
from pathlib import Path
from typing import Any


def parse_roi(value: str) -> tuple[int, int, int, int]:
    try:
        parts = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ROI must be x,y,width,height") from exc
    if len(parts) != 4 or parts[0] < 0 or parts[1] < 0 or parts[2] <= 0 or parts[3] <= 0:
        raise argparse.ArgumentTypeError("ROI must be non-negative x,y and positive width,height")
    return parts


def crossing_evidence(
    history: deque[dict[str, float]],
    chosen: dict[str, float],
    rim_x: float,
    rim_y: float,
    hoop_width: float,
    hoop_height: float,
    max_crossing_time: float,
) -> tuple[dict[str, float], list[dict[str, float]], float] | None:
    corridor_left = rim_x - 0.75 * hoop_width
    corridor_right = rim_x + 0.75 * hoop_width
    below = (
        corridor_left <= chosen["x"] <= corridor_right
        and chosen["y"] >= rim_y + 0.55 * hoop_height
    )
    if not below:
        return None
    above_points = [
        point
        for point in history
        if corridor_left <= point["x"] <= corridor_right
        and point["y"] <= rim_y - 0.15 * hoop_height
        and 0 < chosen["time"] - point["time"] <= max_crossing_time
    ]
    if not above_points:
        return None
    above = above_points[-1]
    if chosen["y"] - above["y"] < 0.70 * hoop_height:
        return None

    crossing_points = [point for point in history if point["time"] >= above["time"]]
    downward_steps = sum(
        1
        for first, second in zip(crossing_points, crossing_points[1:])
        if second["y"] > first["y"]
    )
    step_count = max(1, len(crossing_points) - 1)
    downward_ratio = downward_steps / step_count
    if downward_ratio < 0.60:
        return None
    return above, crossing_points, downward_ratio


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--hoop-roi", required=True, type=parse_roi)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--hsv-lower", default="3,70,60")
    parser.add_argument("--hsv-upper", default="28,255,255")
    parser.add_argument("--motion-threshold", type=int, default=18)
    parser.add_argument("--max-gap", type=float, default=0.30)
    parser.add_argument("--max-crossing-time", type=float, default=1.20)
    parser.add_argument("--dedupe-seconds", type=float, default=2.0)
    parser.add_argument("--pre-roll", type=float, default=4.0)
    parser.add_argument("--post-roll", type=float, default=1.5)
    parser.add_argument("--frame-step", type=int, default=1)
    parser.add_argument("--trace-csv", type=Path)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        print("OpenCV and NumPy are required: install opencv-python and numpy", file=sys.stderr)
        return 2

    def parse_triplet(raw: str, name: str) -> tuple[int, int, int]:
        try:
            values = tuple(int(value.strip()) for value in raw.split(","))
        except ValueError as exc:
            parser.error(f"{name} must contain three integers")
            raise exc
        if len(values) != 3 or any(value < 0 or value > 255 for value in values):
            parser.error(f"{name} must contain three values between 0 and 255")
        return values  # type: ignore[return-value]

    for name in ("max_gap", "max_crossing_time", "dedupe_seconds", "pre_roll", "post_roll"):
        if not math.isfinite(getattr(args, name)) or getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} must be finite and non-negative")
    if args.max_gap == 0 or args.max_crossing_time == 0:
        parser.error("tracking intervals must be positive")
    if args.frame_step < 1:
        parser.error("--frame-step must be at least 1")
    if not 0 <= args.motion_threshold <= 255:
        parser.error("--motion-threshold must be between 0 and 255")

    hsv_lower = np.array(parse_triplet(args.hsv_lower, "--hsv-lower"), dtype=np.uint8)
    hsv_upper = np.array(parse_triplet(args.hsv_upper, "--hsv-upper"), dtype=np.uint8)
    source = args.input.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    output = args.output.expanduser().resolve()
    paths = [output]
    if args.trace_csv:
        paths.append(args.trace_csv.expanduser().resolve())
    if len(set(paths)) != len(paths):
        raise ValueError("events and trace must use different output paths")
    for path in paths:
        if path == source or (path.exists() and path.samefile(source)):
            raise ValueError("output must not overwrite the source video")
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"output exists: {path}; use --overwrite intentionally")

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"cannot open video: {source}")
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if not math.isfinite(fps) or fps <= 0:
        raise RuntimeError("video reports an invalid frame rate")

    hx, hy, hw, hh = args.hoop_roi
    if hx + hw > width or hy + hh > height:
        raise ValueError(f"hoop ROI {args.hoop_roi} exceeds frame size {width}x{height}")
    rim_x = hx + hw / 2.0
    rim_y = hy + hh / 2.0
    search_x0 = max(0, int(hx - 2.5 * hw))
    search_x1 = min(width, int(hx + 3.5 * hw))
    search_y0 = max(0, int(hy - 6.0 * hh))
    search_y1 = min(height, int(hy + 4.0 * hh))
    min_radius = max(2.0, hw * 0.035)
    max_radius = max(min_radius + 1.0, hw * 0.48)

    previous_gray = None
    history: deque[dict[str, float]] = deque()
    trace: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    last_event_time = -1e9
    frame_index = -1
    next_progress_time = 10.0
    kernel = np.ones((3, 3), np.uint8)

    previous_timestamp = None
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        frame_index += 1
        if frame_index % args.frame_step:
            continue
        timestamp = float(capture.get(cv2.CAP_PROP_POS_MSEC)) / 1000.0
        if (not math.isfinite(timestamp) or timestamp < 0 or
                (previous_timestamp is not None and timestamp <= previous_timestamp)):
            capture.release()
            raise RuntimeError("decoder did not provide increasing presentation timestamps; use visual review")
        previous_timestamp = timestamp
        if args.progress and timestamp >= next_progress_time:
            print(
                f"processed {frame_index}/{frame_count or '?'} frames; candidates={len(events)}",
                file=sys.stderr,
            )
            next_progress_time += 10.0
        crop = frame[search_y0:search_y1, search_x0:search_x1]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        if previous_gray is None:
            previous_gray = gray
            continue

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
        difference = cv2.absdiff(gray, previous_gray)
        _, motion_mask = cv2.threshold(
            difference, args.motion_threshold, 255, cv2.THRESH_BINARY
        )
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=2)
        mask = cv2.bitwise_and(color_mask, motion_mask)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        previous_gray = gray

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates: list[dict[str, float]] = []
        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area <= 0:
                continue
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            if radius < min_radius or radius > max_radius:
                continue
            perimeter = float(cv2.arcLength(contour, True))
            circularity = 4.0 * math.pi * area / (perimeter * perimeter) if perimeter else 0.0
            fill = area / (math.pi * radius * radius)
            if circularity < 0.25 or fill < 0.20:
                continue
            full_x = float(cx + search_x0)
            full_y = float(cy + search_y0)
            horizontal_distance = abs(full_x - rim_x) / max(hw, 1)
            corridor_score = max(0.0, 1.0 - horizontal_distance / 2.0)
            quality = min(1.0, 0.45 * circularity + 0.35 * fill + 0.20 * corridor_score)
            candidates.append(
                {"time": timestamp, "x": full_x, "y": full_y, "quality": quality}
            )

        chosen = None
        if candidates:
            if history and timestamp - history[-1]["time"] <= args.max_gap:
                previous = history[-1]
                chosen = min(
                    candidates,
                    key=lambda item: math.hypot(
                        item["x"] - previous["x"], item["y"] - previous["y"]
                    )
                    / max(hw, 1)
                    - 0.35 * item["quality"],
                )
            else:
                chosen = max(candidates, key=lambda item: item["quality"])

        if chosen is not None:
            if history and timestamp - history[-1]["time"] > args.max_gap:
                history.clear()
            history.append(chosen)
            if args.trace_csv:
                trace.append({"frame": frame_index, **chosen})
        while history and timestamp - history[0]["time"] > args.max_crossing_time:
            history.popleft()

        if chosen is None or timestamp - last_event_time < args.dedupe_seconds:
            continue

        evidence = crossing_evidence(
            history, chosen, rim_x, rim_y, hw, hh, args.max_crossing_time
        )
        if evidence is None:
            continue
        above, crossing_points, downward_ratio = evidence

        mean_quality = sum(point["quality"] for point in crossing_points) / len(crossing_points)
        continuity = min(1.0, len(crossing_points) / 4.0)
        centrality = max(
            0.0, 1.0 - abs(chosen["x"] - rim_x) / max(hw * 0.75, 1)
        )
        confidence = min(
            0.84,
            0.40 + 0.20 * mean_quality + 0.15 * continuity + 0.09 * centrality,
        )
        event_number = len(events) + 1
        events.append(
            {
                "id": f"score-{event_number:04d}",
                "source": str(source),
                "result": "made_candidate",
                "confidence": round(confidence, 4),
                "candidate_start": round(max(0.0, timestamp - args.pre_roll), 6),
                "release_time": None,
                "score_time": round(timestamp, 6),
                "clip_start": round(max(0.0, timestamp - args.pre_roll), 6),
                "clip_end": round(timestamp + args.post_roll, 6),
                "evidence": {
                    "above_rim_time": round(above["time"], 6),
                    "below_rim_time": round(chosen["time"], 6),
                    "downward_crossing": True,
                    "downward_ratio": round(downward_ratio, 4),
                    "track_points": len(crossing_points),
                    "hoop_roi": list(args.hoop_roi),
                },
                "review": {"status": "pending", "notes": "fixed-camera baseline"},
            }
        )
        last_event_time = timestamp
        history.clear()

    capture.release()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "version": 1,
        "source": str(source),
        "detector": {
            "name": "fixed-camera-baseline",
            "mode": "candidate-only",
            "frame_size": [width, height],
            "fps": fps,
            "timebase": "decoder-presentation-timestamps",
            "hoop_roi": list(args.hoop_roi),
        },
        "events": events,
    }
    with output.open("w" if args.overwrite else "x", encoding="utf-8") as handle:
        handle.write(json.dumps(document, indent=2, ensure_ascii=False) + "\n")

    if args.trace_csv:
        trace_path = args.trace_csv.expanduser().resolve()
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with trace_path.open("w" if args.overwrite else "x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=("frame", "time", "x", "y", "quality")
            )
            writer.writeheader()
            writer.writerows(trace)

    print(json.dumps({"output": str(output), "candidates": len(events)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
