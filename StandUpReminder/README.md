# StandUpReminder（iOS）

一个使用 SwiftUI + 本地通知的苹果手机提醒 App：每 20 分钟提醒你站起来活动，防止久坐。

## 功能
- 首次启动请求通知权限。
- 打开开关后，每 20 分钟推送一次提醒通知。
- 可随时关闭提醒。

## 使用方式
1. 用 Xcode 新建一个 iOS App 工程（SwiftUI）。
2. 将本目录下的 `StandUpReminderApp.swift`、`ContentView.swift`、`ReminderManager.swift` 覆盖到工程同名文件。
3. 在真机上运行（通知在真机体验更完整）。
4. 首次授权通知后，打开“开启 20 分钟提醒”。

## 说明
- 这是本地通知方案，无需后端。
- iOS 通知展示受系统策略影响（如专注模式、通知摘要等）。
