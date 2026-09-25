# Changelog / 版本变更记录

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
