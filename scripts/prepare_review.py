#!/usr/bin/env python3
"""Create a bounded, local SDR review proxy with an explicit source-time mapping."""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

from clip_events import probe_media, protect_output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--start', type=float, default=0)
    parser.add_argument('--duration', type=float, default=60)
    args = parser.parse_args()
    if not math.isfinite(args.start) or args.start < 0:
        parser.error('--start must be finite and non-negative')
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error('--duration must be finite and positive')
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        parser.error('ffmpeg and ffprobe are required on PATH')
    source = args.input.expanduser().resolve()
    media = probe_media(ffprobe, source)
    if args.start >= media['duration']:
        parser.error('--start is outside the video')
    duration = min(args.duration, media['duration'] - args.start)
    directory = args.output_dir.expanduser().resolve()
    proxy, mapping = directory / 'review.mp4', directory / 'source-map.json'
    for path in (proxy, mapping):
        protect_output(path, {source}, False)
    directory.mkdir(parents=True, exist_ok=True)
    filters = []
    if media['hdr']:
        available = subprocess.run([ffmpeg, '-hide_banner', '-filters'],
                                   capture_output=True, text=True, check=True).stdout
        if not all(name in available for name in ('zscale', 'tonemap')):
            raise RuntimeError('HDR preview needs an FFmpeg build with zscale and tonemap; use verified editor HDR handling instead')
        # Explicit SDR viewing derivative; source metadata is retained in the map.
        filters += ['zscale=t=linear:npl=100', 'format=gbrpf32le',
                    'zscale=p=bt709', 'tonemap=tonemap=hable:desat=0',
                    'zscale=t=bt709:m=bt709:r=tv', 'format=yuv420p']
    filters += ["scale=w='min(1280,iw)':h='min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2", 'setsar=1']
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
               '-ss', str(args.start), '-i', str(source), '-t', str(duration),
               '-map', '0:v:0', '-map', '0:a:0?', '-vf', ','.join(filters),
               '-fps_mode', 'vfr', '-c:v', 'libx264', '-preset', 'veryfast',
               '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
               '-map_metadata', '-1', '-movflags', '+faststart']
    if media['hdr']:
        command += ['-color_trc', 'bt709', '-colorspace', 'bt709', '-color_primaries', 'bt709']
    command += [str(proxy)]
    subprocess.run(command, check=True)
    proxy_media = probe_media(ffprobe, proxy)
    if abs(proxy_media['duration'] - duration) > 0.5:
        raise RuntimeError('proxy duration mismatch; do not use this proxy for event timing')
    document = {'version': 1, 'source': str(source), 'proxy': str(proxy),
                'source_start': args.start, 'requested_duration': duration,
                'proxy_duration': proxy_media['duration'],
                'time_mapping': 'source_seconds = proxy_seconds + source_start',
                'purpose': 'visual-review-only', 'source_media': media,
                'hdr_to_sdr_preview': media['hdr'], 'command': command}
    with mapping.open('x', encoding='utf-8') as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps(document, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
