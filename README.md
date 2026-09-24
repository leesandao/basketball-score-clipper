# basketball-score-clipper

一个面向 Codex 的本地篮球进球识别与自动剪辑 Skill。目标不是只保留篮球入网的一瞬间，而是输出从投篮准备/出手、飞行到进球结束的完整片段。

当前版本是 **v0.1 MVP**：固定机位可以通过颜色、运动和篮筐穿越轨迹生成待复核的进球候选；复杂比赛需要接入训练好的篮球/篮筐检测器。

## 能力

- 扫描本地篮球视频并生成统一的事件 JSON。
- 固定机位、单篮筐场景的 CPU 候选检测。
- 保留出手前上下文和进球后余量。
- 按置信度区分自动接受、人工复核和忽略事件。
- 使用 FFmpeg 逐段精确剪辑，自动选择 NVENC、VideoToolbox 或 CPU 编码器。
- 不覆盖原始视频。
- 可配合 [`ffmpeg-skill`](https://github.com/kajisho5/ffmpeg-skill) 做 HDR、拼接和画面质检。

## 安装

将仓库放到 Codex 的个人 skills 目录：

```bash
gh repo clone leesandao/basketball-score-clipper ~/.codex/skills/basketball-score-clipper
```

重新开始一个 Codex 对话后，可以直接调用：

```text
使用 $basketball-score-clipper 找出 input 目录中的进球，并剪出从出手到入网后的完整片段。
```

## 运行依赖

剪辑需要：

- Python 3.9+
- FFmpeg 与 FFprobe

固定机位候选检测另外需要：

```bash
python3 -m pip install -r requirements-detect.txt
```

训练模型推理可以使用 CPU；有 NVIDIA CUDA 时优先使用 GPU。RTX 3060 12GB 足以承担面向单路视频的检测和二阶段复核。

检查当前环境：

```bash
python3 scripts/preflight.py --json
```

## 快速开始

初始化项目：

```bash
python3 scripts/init_project.py --root /path/to/basketball-project
```

固定机位候选检测需要先从代表帧确认篮筐 ROI：

```bash
python3 scripts/detect_fixed_camera.py \
  --input /path/to/input/game.mp4 \
  --hoop-roi x,y,width,height \
  --output /path/to/events/game.json
```

生成待复核片段：

```bash
python3 scripts/clip_events.py \
  --events /path/to/events/game.json \
  --output-dir /path/to/review \
  --include-candidates \
  --min-confidence 0.55
```

复核后，将真实进球的 `result` 改成 `made`，再输出最终片段：

```bash
python3 scripts/clip_events.py \
  --events /path/to/events/game.json \
  --output-dir /path/to/clips
```

事件格式见 [`references/event-schema.md`](references/event-schema.md)。检测模式和适用边界见 [`references/detection-modes.md`](references/detection-modes.md)。

## 当前限制

- 固定机位检测器只负责产生候选，不会把候选自动冒充为已确认进球。
- 手持、变焦、多人遮挡、逆光和远距离小球需要训练模型。
- 如果画面没有拍到投篮人，只能估算剪辑起点，不能准确恢复出手帧。
- HDR 素材不会被静默转换成 SDR；请使用 HDR-aware 工作流处理。
- 当前版本尚未直接写入剪映草稿；可以先生成 MP4 片段，再导入剪映。

## 开发

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

路线图：

1. 篮球与篮筐专用检测模型接口。
2. 球轨迹跟踪和短暂遮挡恢复。
3. 人体姿态辅助出手时间检测。
4. 可视化候选复核页面。
5. 剪映/CapCut 草稿输出。

## License

MIT
