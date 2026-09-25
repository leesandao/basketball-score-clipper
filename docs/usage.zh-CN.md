# 使用指南

[English](usage.en.md) · [返回首页](../README.md)

## 1. 安装与环境

按照首页克隆仓库并创建虚拟环境。macOS 可用 `brew install ffmpeg`；Ubuntu/Debian 可用 `sudo apt-get install ffmpeg`。确保 `ffmpeg` 与 `ffprobe` 都在 PATH 中。

在虚拟环境已激活、当前目录为 Skill 根目录时运行：

```bash
python scripts/preflight.py --json --require-detection
```

只导出已有事件 JSON 时不用安装 OpenCV，也不要求 FFmpeg。`preflight.py` 检查的是媒体处理环境，并非表格导出的必要前置步骤。

为让后续对话找到独立虚拟环境，可在 Skill 根目录写入本机专用配置（已被 Git 忽略）：

```bash
python - <<'PY'
import json, shutil, sys
from pathlib import Path
ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise SystemExit('Install FFmpeg and add it to PATH first')
Path('runtime.json').write_text(json.dumps({
    'python': sys.executable,
    'bin_dir': str(Path(ffmpeg).parent)
}, indent=2) + '\n')
PY
```

## 2. 准备素材

- 输入为本地文件或已经挂载的 NAS 文件路径，例如 `/path/to/game.mp4`。
- 输出放在独立目录；不要将原视频当成输出文件。
- 从 `00:00:00` 开始计算视频播放时间，不使用拍摄日期或墙上时钟。
- 先读取总时长、旋转和帧率信息，确认视频是否分段变焦或移动机位。

```bash
ffprobe -v error -show_format -show_streams -of json /path/to/game.mp4
```

## 3. 使用 Skill

```text
使用 $basketball-score-clipper 分析 /path/to/game.mp4。
以原视频播放时间为基准，只标记球进入篮筐的瞬间。
输出进球时间表和剪映 SRT 字幕定位标记。
不确定的候选单独列出，输出写入 /path/to/output，不剪辑视频。
```

智能体会查看代表帧来确定篮筐 ROI，运行检测并复核候选附近的连续帧。大幅移动机位时，必须重新确定 ROI 或改用人工检查。默认不启动剪映、不生成预览、不导出视频。

## 4. 命令行：筛选候选

以下 ROI 数值仅是语法示例，必须替换为查看自己视频后得到的 `x,y,width,height`：

```bash
python scripts/detect_fixed_camera.py \
  --input /path/to/game.mp4 \
  --hoop-roi 300,200,80,30 \
  --output /path/to/output/candidates.json --progress
```

ROI 使用旋转后显示画面的像素坐标。保持默认 `--frame-step 1`，避免跳过短暂的入筐瞬间。脚本仍需解码视频；限制图像处理区域不等于省去解码或 NAS 读取成本。

检测结果全部为 `made_candidate`。脚本不会自动判断真实进球；请由人工或有视觉能力的智能体复核，并把编辑后的 JSON 另存为 `reviewed-events.json`。

## 5. 复核并记录入筐时间

1. 查看候选前后连续帧，确认球从上向下进入篮圈并继续穿过篮网。
2. 找到首次可见入筐的帧，将原片秒数填入 `basket_entry_time`。
3. 明确帧位置使用 `entry_time_basis: observed_frame`；只能估算时用 `estimated` 并在备注说明误差区间。
4. 已确认进球设为 `result: made`、`review.status: accepted`；误检设为 `miss` 或 `rejected`；不确定保留待复核。
5. 保留原有 `confidence` 和 `score_time`。`score_time` 是检测器确认穿越的较晚时刻，不一定等于入筐瞬间。

完整合成示例见 [examples/reviewed-events.json](../examples/reviewed-events.json)，字段定义见 [事件格式](../references/event-schema.md)。

## 6. 输出时间表与 SRT

下面的 120 秒为示例视频时长；自己的视频请用 FFprobe 的实际结果：

```bash
python scripts/export_timestamps.py \
  --events /path/to/output/reviewed-events.json \
  --output /path/to/output/basket-timestamps.md \
  --srt /path/to/output/basket-markers.srt \
  --duration 120 --include-pending
```

- Markdown 中默认只有已确认进球；`--include-pending` 追加独立的待复核表。
- SRT 永远只包含已确认进球，且要求已记录 `basket_entry_time`。
- 多视频 JSON 需用 `--source` 指定与 JSON 完全一致的源路径，每个视频单独导出一个 SRT。
- `--marker-duration` 默认 1 秒，标记结束会裁到下一个标记或原视频结束。
- 输出文件存在时拒绝覆盖，请换文件名。零个已确认进球会产生空 SRT，无需导入。
- 时间码带毫秒不表示识别精度达到毫秒；实际精度取决于原视频帧率、清晰度和复核证据。

## 7. 剪映定位

1. 将对应原视频放在时间线零点，保持原速，先不要剪切。
2. 「字幕」→「新建字幕」→「导入本地字幕」，选择 SRT。
3. 保持播放头在零点，点击字幕素材右下角添加按钮，加入辅助字幕轨。
4. 对照表格检查首条标记时间；字幕条左边缘对应入筐点，供人工快速定位。
5. 剪辑完成后隐藏或删除辅助字幕轨。

这是字幕式标记，不是剪映原生旗形标记。如果原片已经裁切、拼接或变速，应先建立时间换算关系。不要直接修改未公开的剪映草稿 JSON。

## 8. 可选剪辑与常见问题

明确需要成片时才使用 [剪辑流程](../references/clipping-workflow.md)。HDR 原片不会被默认转换成 SDR；短预览的 HDR 色调映射还要求 FFmpeg 包含 `zscale` 和 `tonemap`，否则使用经核对的编辑器流程。

| 问题 | 处理 |
| --- | --- |
| 找不到 Skill | 新一轮对话调用，或提供 `SKILL.md` 的绝对路径 |
| 找不到依赖 | 激活虚拟环境，核对 PATH 与 `runtime.json` |
| 没检测到或误检很多 | 核对旋转后的 ROI、球尺寸、光线与机位；不要靠提高置信度代替复核 |
| 旧事件不能导出 SRT | 补充 `basket_entry_time`；不要直接复制较晚的 `score_time` |
| NAS 读取慢 | 检查挂载和网络，复用检测结果；不承诺快于实时 |
| 时间码超出时长 | 核对源文件、代理偏移与传入的 `--duration` |

## 从 v0.1.0 升级

默认产物从视频片段变为时间表＋SRT，调用名不变。旧 JSON 仍可显示确认时刻，但需要补充入筐时间才能导出 SRT。旧的剪辑脚本仍保留，仅在明确请求时使用。更新前保留自己的修改；不要覆盖本机 `runtime.json`。
