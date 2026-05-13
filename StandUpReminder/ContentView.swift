import SwiftUI

struct ContentView: View {
    @StateObject private var manager = ReminderManager()

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 24) {
                Text("防久坐提醒")
                    .font(.largeTitle).bold()

                Text("每 20 分钟提醒你站起来活动一下，减少久坐带来的健康风险。")
                    .font(.body)

                if manager.permissionGranted {
                    Toggle("开启 20 分钟提醒", isOn: Binding(
                        get: { manager.reminderEnabled },
                        set: { enabled in
                            if enabled {
                                manager.enableReminder()
                            } else {
                                manager.disableReminder()
                            }
                        })
                    )
                    .toggleStyle(.switch)
                } else {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("需要通知权限才能发送提醒。")
                        Button("授权通知") {
                            manager.requestPermission()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("Stand Up")
        }
        .task {
            await manager.refreshSettings()
        }
    }
}

#Preview {
    ContentView()
}
