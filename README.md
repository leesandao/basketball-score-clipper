# Basketball Score Clipper

[English](README.en.md) · **简体中文**

[![Tests](https://github.com/leesandao/basketball-score-clipper/actions/workflows/test.yml/badge.svg)](https://github.com/leesandao/basketball-score-clipper/actions/workflows/test.yml)
[![Version](https://img.shields.io/github/v/release/leesandao/basketball-score-clipper)](https://github.com/leesandao/basketball-score-clipper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

面向 Codex 的本地篮球视频 Skill。**v0.2.0 默认找出球进入篮筐的时间，输出进球时间表和可导入剪映的 SRT 字幕定位标记，供人工快速定位剪辑。** 调用名称继续使用 `$basketball-score-clipper`。

不需要独立 GPU。默认直接分析本地或已挂载 NAS 的原视频，不生成代理视频或集锦。仅在明确要求时启用视频剪辑。

## 工作方式

读取视频参数与总时长 → 确认篮筐区域 → CPU 筛选候选 → 复核候选附近连续帧 → 定位入筐时刻 → 输出表格和 SRT。

**候选检测不等于进球确认。** 内置检测器采用颜色、运动和轨迹规则，不包含训练模型；误检、遮挡与漏检仍可能发生。复核由使用 Skill 的智能体或人工完成，Python 脚本不自动完成视觉确认。尚无全场准确率或召回率基准。

## 输出

| 文件 | 用途 |
| --- | --- |
| `reviewed-events.json` | 原片时间、检测证据、复核状态和入筐时间 |
| `basket-timestamps.md` | 按时间排列的进球表格，含时间码、秒数和估算说明 |
| `basket-markers.srt` | 导入剪映后作为辅助字幕轨定位，条目左边缘为入筐时间 |

SRT 是**字幕式定位标记，不是剪映原生旗形标记**。默认每条持续一秒；未确认候选不写入 SRT。原视频须在时间线零点开始、保持原速；已裁切、拼接或变速的时间线需要另外换算。

## 适用场景

| 场景 | 适用程度 |
| --- | --- |
| 固定机位、单篮筐、橙色球清晰 | 适合内置 CPU 候选检测，仍须复核 |
| 已知时间点或已复核事件 JSON | 可直接生成时间表与 SRT，无需再次扫描 |
| 本地或挂载 NAS 的长视频 | 可直接读取；速度受解码、网络和候选数量影响 |
| 手持、平移、变焦或多个篮筐 | 需分段重新确认 ROI、人工检查或外接训练模型 |
| 小球、逆光、模糊和严重遮挡 | 无法保证准确率，不宜无人值守自动确认 |

详见 [适用场景与限制](docs/use-cases.zh-CN.md)。

## 安装与调用

需要 Python 3.11+。完整流程需要 FFmpeg/FFprobe，CPU 检测另需 OpenCV 和 NumPy。已有事件 JSON 的表格/SRT 导出只需 Python 标准库。

```bash
git clone https://github.com/leesandao/basketball-score-clipper.git "$HOME/.codex/skills/basketball-score-clipper"
cd "$HOME/.codex/skills/basketball-score-clipper"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-detect.txt
```

FFmpeg 安装、独立虚拟环境配置及首次检查见 [中文使用指南](docs/usage.zh-CN.md)。安装后在新一轮对话中调用；如未被发现，可直接提供本仓库 `SKILL.md` 的绝对路径。

```text
使用 $basketball-score-clipper 分析 /path/to/game.mp4，
只输出进球时间点表格和可导入剪映的 SRT 定位文件。
按原视频时间定位，复核球进入篮筐的瞬间。
不确定的候选单独列出，不剪辑或导出视频。
```

纯命令行导出示例（示例数据为合成数据，无需视频）：

```bash
python scripts/export_timestamps.py \
  --events examples/reviewed-events.json \
  --output /tmp/basket-timestamps.md \
  --srt /tmp/basket-markers.srt --duration 120
```

输出路径必须尚不存在；`--duration` 应为对应原视频真实总时长。

## 剪映导入

已在剪映专业版 11.4.2 macOS 验证：**字幕 → 新建字幕 → 导入本地字幕 → 选择 SRT → 点击字幕素材右下角添加按钮**。导入后核对首条标记是否与表格一致。人工剪辑完成后隐藏或删除辅助字幕轨，避免把定位文字渲染进成片。

详见 [SRT 导入说明](references/jianying-markers.md)。

## 文档

- [中文使用指南](docs/usage.zh-CN.md) / [English guide](docs/usage.en.md)
- [适用场景与限制](docs/use-cases.zh-CN.md) / [Use cases and limitations](docs/use-cases.en.md)
- [版本变更记录（中英文）](CHANGELOG.md)
- [事件格式](references/event-schema.md) · [检测模式](references/detection-modes.md)
- [可选视频剪辑](references/clipping-workflow.md) · [贡献指南（中英文）](CONTRIBUTING.md)

## 开发与验证

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

媒体集成测试需要 FFmpeg/FFprobe，检测测试需要 OpenCV；缺少依赖时相应测试跳过。CI 安装这些依赖后运行全部测试。不要提交原片、真实比赛的导出数据或本机 `runtime.json`。

采用 [MIT License](LICENSE)。
