#!/usr/bin/env python3
"""Report dependencies and acceleration available to basketball-score-clipper."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from typing import Any


def command_version(command: str) -> dict[str, Any]:
    path = shutil.which(command)
    result: dict[str, Any] = {"available": bool(path), "path": path}
    if not path:
        return result
    try:
        proc = subprocess.run(
            [path, "-version"], capture_output=True, text=True, timeout=10, check=False
        )
        first = (proc.stdout or proc.stderr).splitlines()
        result["version"] = first[0] if first else "unknown"
    except (OSError, subprocess.SubprocessError) as exc:
        result["error"] = str(exc)
    return result


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def available_encoders(ffmpeg_path: str | None) -> list[str]:
    if not ffmpeg_path:
        return []
    try:
        proc = subprocess.run(
            [ffmpeg_path, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    text = proc.stdout + proc.stderr
    return [name for name in ("h264_nvenc", "h264_videotoolbox", "libx264") if name in text]


def cuda_status() -> dict[str, Any]:
    status: dict[str, Any] = {
        "nvidia_smi": bool(shutil.which("nvidia-smi")),
        "torch_installed": module_available("torch"),
        "torch_cuda_available": False,
    }
    if status["torch_installed"]:
        try:
            import torch  # type: ignore

            status["torch_cuda_available"] = bool(torch.cuda.is_available())
            if status["torch_cuda_available"]:
                status["device_count"] = int(torch.cuda.device_count())
                status["devices"] = [
                    torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
                ]
        except Exception as exc:  # dependency diagnostics should not crash preflight
            status["torch_error"] = str(exc)
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--require-detection",
        action="store_true",
        help="fail unless OpenCV and NumPy for the fixed-camera detector are available",
    )
    parser.add_argument(
        "--require-cuda", action="store_true", help="fail unless PyTorch can use CUDA"
    )
    args = parser.parse_args()

    ffmpeg = command_version("ffmpeg")
    ffprobe = command_version("ffprobe")
    modules = {
        "opencv": module_available("cv2"),
        "numpy": module_available("numpy"),
        "torch": module_available("torch"),
        "ultralytics": module_available("ultralytics"),
    }
    cuda = cuda_status()
    report = {
        "ready_for_clipping": bool(ffmpeg["available"] and ffprobe["available"]),
        "ready_for_fixed_camera_detection": bool(modules["opencv"] and modules["numpy"]),
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "encoders": available_encoders(ffmpeg.get("path")),
        "python_modules": modules,
        "cuda": cuda,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")

    if not report["ready_for_clipping"]:
        return 2
    if args.require_detection and not report["ready_for_fixed_camera_detection"]:
        return 3
    if args.require_cuda and not cuda["torch_cuda_available"]:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
