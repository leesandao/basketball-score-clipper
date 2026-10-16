# Changelog / 版本变更记录

## v0.3.1 — 2026-10-16

### 中文

- 放大慢放默认跟随持球进攻球员，覆盖突破、对抗、出手与落地；分屏时保留同步全场视角。专门的篮筐特写按明确要求使用。
- 球权转换时跟随接球者或实际补篮得分者；出手后保持球员特写，保留身体、手与球、脚步及出手空间。
- 记录原片时间与裁切关键帧，平滑插值并映射到慢放；遮挡或跟随不清时扩大取景，逐球复核实际导出画面。
- 同步中英文指南和调用示例。仅更新 Skill 与文档，不新增自动球员跟踪器，默认时间表＋SRT模式不变。

### English

- Make enlarged slow motion follow the ball-handling attacker through the drive, contest, release and landing, with a synchronized wide view in split layouts. Use dedicated hoop close-ups when explicitly requested.
- Follow possession to receivers or actual put-back scorers; stay with the player after release and preserve body, hands/ball, footwork and release margins.
- Record source-time crop keyframes, interpolate smoothly and map to replay speed; widen unclear framing and review every exported replay.
- Update bilingual guides and request examples. Guidance only: no automatic player tracker is added, and timestamp/SRT output remains the default.

## v0.3.0 — 2026-10-12

### 中文

根据实际集锦制作与纠错过程，补充显式视频请求的选片、声音与更正流程。默认时间表＋SRT模式不变；本版主要更新Skill与文档，不新增训练模型或自动集锦脚本。

- 入选镜头及实际导出成片必须重新核对穿筐路径；明确篮网前方下落、网兜晃动与旧接受标签都不能单独证明进球。
- 区分出手者、助攻与补篮者；三分核对起跳前脚位，选片兼顾贴防、身体对抗、补防及球员覆盖。
- 按球衣/号码记录临时球员分组，覆盖请求优先每位一个确认进球；找不到未出场新球员时说明限制并确认替代方式。
- 区分播放段序与NO.排名，避免在倒数集锦里替换错误的球。
- 添加歌曲时保留现场原声；正式曲目、试听、署名、实际节拍相位、时间映射与替换后卡点复核纳入流程。
- 用户指出错球时撤销旧确认，并同步事件JSON、时间表、SRT与成片；保留更正来源，不把局部修改说成全量复核。
- 新增中英文集锦指南及可选事件字段说明，提供可配置的“3个三分＋7个对抗”示例。

### English

Document selection, sound and correction lessons from real editing sessions. Timestamp/SRT output remains the default. This release updates skill guidance and documentation; it adds no trained detector or automatic montage script.

- Recheck selected source attempts and rendered baskets; front-of-net misses, net motion and stale acceptances cannot independently establish a make.
- Distinguish scorers, assists and put-backs; verify three-point takeoff positions and balance close defense, contact, help defense and player coverage.
- Track local jersey/clothing groups, reserve confirmed makes for coverage requests, and explain/resolve unavailable previously unseen players.
- Distinguish playback position from NO. rank in countdown revisions.
- Preserve court sound when adding songs; document actual tracks, listening, attribution, recorded beat phase, time mapping and post-replacement alignment.
- Withdraw wrong acceptances and refresh event JSON, tables, SRT and video outputs, retaining correction provenance without claiming a full re-review.
- Add bilingual highlight guides, optional event metadata and a configurable three-pointer/contested-finish example.

## v0.2.0 — 2026-09-25

### 中文

默认工作流改为定位进球瞬间，交付时间点表格和可导入剪映的 SRT 字幕定位标记。只有明确要求时才生成视频集锦。

- 新增 `export_timestamps.py`：按源视频和时间排序输出 Markdown 表格；可单独列出待复核候选。
- 新增 SRT 导出：只包含人工或视觉复核通过、具有 `basket_entry_time` 的进球；支持选择源视频，限制字幕时长和视频边界。
- 区分入筐瞬间 `basket_entry_time` 与检测确认时间 `score_time`，标明观察帧或估计时间依据。旧 JSON 可继续生成表格；导出 SRT 前需补齐入筐时间。
- CPU 流程优先直接读取原片，按视频时长规划完整覆盖并复核候选附近画面；代理视频与剪辑改为可选步骤。
- 新增可选代理视频准备工具、源文件映射与变帧率时间检查。
- 修复低置信度但已接受事件被过滤、待复核事件被误接纳、硬件编码器不可用时缺少回退、越界剪辑和输出覆盖输入等问题。
- 新增中英文使用指南、适用场景、合成事件示例和媒体集成测试。

兼容性与限制：SRT 在剪映中显示为字幕块，不是原生旗标。已验证 macOS 剪映 11.4.2 的导入流程；其他版本及 CapCut 需自行确认菜单和行为。检测器只提供候选，不保证全部进球召回；没有新增训练模型或准确率基准。时间点导出不需要 GPU。

### English

The default workflow now locates made-basket moments and delivers a timestamp table plus SRT subtitle cues for editor navigation. Highlight rendering requires an explicit request.

- Add `export_timestamps.py` for chronological Markdown tables grouped by source, with optional pending-review rows.
- Add SRT export for accepted made baskets with `basket_entry_time`, source selection, bounded cue duration, and video-boundary checks.
- Separate basket-entry time from detection-confirmation time (`score_time`), recording whether timing is observed or estimated. Legacy JSON remains usable for tables; add basket-entry times before SRT export.
- Prefer direct CPU analysis of originals, plan coverage against video duration, and review frames around candidates. Proxies and clip rendering are optional.
- Add optional proxy preparation, source mapping, and variable-frame-rate timing checks.
- Fix filtering of accepted low-confidence events, unintended acceptance of pending events, unavailable hardware-encoder fallback, invalid clip bounds, and outputs overwriting inputs.
- Add bilingual usage and use-case documentation, synthetic event examples, and media integration tests.

Compatibility and limitations: SRT appears as subtitle blocks, not native timeline flags. Import was verified in Jianying 11.4.2 on macOS; other versions and CapCut require their own menu and behavior checks. The detector produces candidates and does not guarantee complete recall. This release adds no trained model or accuracy benchmark. Timestamp export requires no GPU.

## v0.1.0

- 中文：初始版本，提供进球事件结构、固定机位候选检测和基于事件的集锦剪辑工具。
- English: Initial release with a scoring-event schema, fixed-camera candidate detection, and event-based highlight clipping tools.
