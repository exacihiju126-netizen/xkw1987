# Xcode / iOS SDK 安装说明（当前环境）

## 结论
当前容器是 **Ubuntu Linux**，无法原生安装 Xcode 或 iOS SDK。

- Xcode 仅由 Apple 提供，官方仅支持安装在 macOS。
- iOS Simulator 依赖 Xcode 与 macOS 框架，不能在 Linux 容器运行。

## 本环境检测信息
- `uname -a` 显示 Linux 内核。
- `/etc/os-release` 显示 Ubuntu 24.04.4 LTS。

## 可行替代方案
1. 使用一台 Mac（本地或云 Mac）安装 Xcode：
   - App Store 安装 Xcode（推荐）
   - 或 `xcode-select --install` 安装命令行工具
2. 在 Mac 上打开本仓库中的 `StandUpReminder` 代码并创建 iOS App Target 运行。
3. 若只做静态检查，可在 Linux 安装 Swift 工具链进行部分语法验证（不含 iOS SDK/模拟器能力）。

## 如果你希望我继续
我可以下一步帮你：
- 生成完整可直接打开的 Xcode 工程结构（`.xcodeproj`）；
- 增加本地通知权限说明（`Info.plist`）和更完善的提醒开关状态恢复；
- 提供在 Mac 上的一键构建命令（`xcodebuild`）与验证清单。
