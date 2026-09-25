#!/usr/bin/env python3
"""Export confirmed basketball entry times as a Markdown table, without media processing."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def seconds(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('timestamp must be a number')
    if not math.isfinite(value) or value < 0:
        raise ValueError('timestamp must be finite and non-negative')
    return float(value)


def timecode(value):
    milliseconds = round(seconds(value) * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    whole, fraction = divmod(remainder, 1000)
    return f'{hours:02d}:{minutes:02d}:{whole:02d}.{fraction:03d}'


def escape(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')


def render(document, include_pending=False):
    if not isinstance(document, dict) or not isinstance(document.get('events'), list):
        raise ValueError('event file must contain an events array')
    accepted, pending, seen = [], [], set()
    for event in document['events']:
        if not isinstance(event, dict):
            raise ValueError('each event must be an object')
        review = event.get('review') or {}
        if not isinstance(review, dict):
            raise ValueError('review must be an object')
        if review.get('status') == 'rejected' or event.get('result') in ('miss', 'rejected'):
            continue
        confirmed = event.get('result') == 'made' and review.get('status') == 'accepted'
        if not confirmed and event.get('result') not in ('made', 'made_candidate'):
            continue
        source = event.get('source') or document.get('source')
        if not isinstance(source, str) or not source:
            raise ValueError('event must have a source')
        identity = (source, event.get('id'))
        if not isinstance(identity[1], str) or not identity[1]:
            raise ValueError('event must have an id')
        if identity in seen:
            raise ValueError(f'duplicate event id for source: {identity}')
        seen.add(identity)
        if event.get('basket_entry_time') is not None:
            timestamp = seconds(event['basket_entry_time'])
            basis = event.get('entry_time_basis', 'estimated')
            if basis not in ('observed_frame', 'estimated'):
                raise ValueError('entry_time_basis must be observed_frame or estimated')
            label = '入筐帧' if basis == 'observed_frame' else '估算入筐时间'
        else:
            timestamp = seconds(event.get('score_time'))
            label = '确认时刻，入筐时间待精定位'
        row = (source, timestamp, label, review.get('notes', ''))
        (accepted if confirmed else pending).append(row)

    def table(rows):
        lines = ['| 序号 | 视频 | 时间点 | 秒数 | 时间依据 | 备注 |',
                 '| --- | --- | --- | --- | --- | --- |']
        for index, (source, timestamp, basis, notes) in enumerate(sorted(rows, key=lambda row: (row[0], row[1])), 1):
            lines.append(f'| {index} | {escape(source)} | {timecode(timestamp)} | {timestamp:.3f} | {escape(basis)} | {escape(notes)} |')
        return '\n'.join(lines)

    parts = ['# 篮球进球时间表', f'已确认 {len(accepted)} 个；待复核 {len(pending)} 个。时间相对于各自原视频开头。']
    parts.append(table(accepted) if accepted else '暂无已确认进球。')
    if include_pending and pending:
        parts += ['## 待复核候选（不计入已确认进球）', table(pending)]
    return '\n\n'.join(parts) + '\n'


def render_srt(document, duration, source=None, marker_duration=1.0):
    duration, marker_duration = seconds(duration), seconds(marker_duration)
    if duration <= 0 or marker_duration <= 0:
        raise ValueError('video duration and marker duration must be positive')
    # Reuse validation; SRT is strictly for confirmed makes with an entry time.
    render(document)
    sources = {event.get('source') or document.get('source') for event in document['events']}
    if not sources and document.get('source'):
        sources.add(document['source'])
    if not document['events']:
        return ''
    if source is None:
        if len(sources) != 1:
            raise ValueError('one SRT must correspond to one video; specify --source')
        source = next(iter(sources))
    if source not in sources:
        raise ValueError('--source does not match any event source')
    rows = []
    for event in document['events']:
        if (event.get('source') or document.get('source')) != source:
            continue
        if event.get('result') != 'made' or (event.get('review') or {}).get('status') != 'accepted':
            continue
        if event.get('basket_entry_time') is None:
            raise ValueError('confirmed events need basket_entry_time before SRT export; do not substitute score_time')
        start = seconds(event['basket_entry_time'])
        if start >= duration:
            raise ValueError('entry time must be within the original video duration')
        rows.append((round(start * 1000), event.get('entry_time_basis', 'estimated')))
    rows.sort()
    blocks = []
    for index, (start, basis) in enumerate(rows):
        end = min(round(duration * 1000), start + round(marker_duration * 1000))
        if index + 1 < len(rows):
            end = min(end, rows[index + 1][0])
        if end <= start:
            raise ValueError('marker times collide or have no duration at millisecond precision')
        label = ' [估算]' if basis != 'observed_frame' else ''
        blocks.append(f'{index + 1}\n{timecode(start / 1000).replace(".", ",")} --> '
                      f'{timecode(end / 1000).replace(".", ",")}\n'
                      f'进球 {index + 1:03d} | {timecode(start / 1000)}{label}\n')
    return '\n'.join(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True, type=Path)
    parser.add_argument('--output', type=Path, help='new Markdown file; existing files are never replaced')
    parser.add_argument('--include-pending', action='store_true')
    parser.add_argument('--srt', type=Path, help='new UTF-8 SRT subtitle marker file, one source per file')
    parser.add_argument('--duration', type=float, help='original video duration in seconds (required for SRT)')
    parser.add_argument('--source', help='exact source value to select when exporting multi-source JSON to SRT')
    parser.add_argument('--marker-duration', type=float, default=1.0)
    args = parser.parse_args()
    document = json.loads(args.events.read_text(encoding='utf-8'))
    markdown = render(document, args.include_pending)
    srt = None
    if args.srt:
        if args.duration is None or args.srt.suffix.lower() != '.srt':
            parser.error('--srt requires a .srt path and --duration in original video seconds')
        srt = render_srt(document, args.duration, args.source, args.marker_duration)
    for path in (args.output, args.srt):
        if path and path.exists():
            raise FileExistsError(path)
    if args.output and args.output.suffix.lower() != '.md':
        parser.error('--output must be a .md file')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as handle:
            handle.write(markdown)
    if args.srt:
        args.srt.parent.mkdir(parents=True, exist_ok=True)
        with args.srt.open('x', encoding='utf-8') as handle:
            handle.write(srt)
    print(markdown, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
