# Contributing / 参与贡献

## 中文

欢迎通过 issue 报告误检、漏检和新的拍摄条件，通过 pull request 提交改进。

问题报告请包含系统和 Python/FFmpeg 版本、视频参数、机位是否固定、篮筐像素大小、光线、期望时间和实际结果。优先提供合成复现素材。不要提交私人视频、NAS 路径、本机 `runtime.json`、凭据或模型权重。

提交前请：

1. 保持原片只读，输出默认不覆盖现有文件。
2. 保留检测候选、复核状态与入筐时间的区别；不要将估计时间描述为逐帧观测结果。
3. 为行为变化增加有意义的测试，并同步中英文文档与变更记录。
4. 算法改动说明适用机位和失败条件；若报告准确率，说明数据集、事件匹配容差、进球事件级 precision/recall 及复核方式。
5. 安装 FFmpeg 和检测依赖后运行下面的检查。没有媒体依赖时部分集成测试会跳过；发布前应运行完整测试。

## English

Use issues to report false positives, missed baskets, and new recording conditions. Submit improvements through pull requests.

Include OS and Python/FFmpeg versions, video metadata, camera movement, hoop size in pixels, lighting, expected timing, and actual results. Prefer synthetic reproduction material. Do not commit private footage, NAS paths, local `runtime.json`, credentials, or model weights.

Before submitting:

1. Keep originals read-only and refuse existing outputs by default.
2. Preserve the distinction between candidates, review status, and basket-entry timing. Do not describe estimated times as frame observations.
3. Add meaningful tests for behavior changes and update both language versions of documentation and the changelog.
4. Describe supported camera conditions and failure cases for algorithm changes. Accuracy reports must identify the dataset, event-matching tolerance, event-level precision/recall, and review method.
5. Install FFmpeg and detection dependencies, then run the checks below. Some integration tests skip without media dependencies; run the full suite before release.

```bash
python3 -m pip install -r requirements-detect.txt
python3 -m compileall -q scripts tests
python3 -m unittest discover -s tests -v
git diff --check
```

By contributing, you agree that your contributions are licensed under this repository's [MIT license](LICENSE).
提交贡献即表示同意以本仓库的 [MIT 许可证](LICENSE) 授权这些贡献。
