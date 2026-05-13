import Foundation
import UserNotifications

final class ReminderManager: ObservableObject {
    @Published var permissionGranted = false
    @Published var reminderEnabled = false

    private let center = UNUserNotificationCenter.current()
    private let reminderId = "standup-reminder-20min"

    init() {
        Task {
            await refreshSettings()
        }
    }

    @MainActor
    func refreshSettings() async {
        let settings = await center.notificationSettings()
        permissionGranted = settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional
    }

    func requestPermission() {
        center.requestAuthorization(options: [.alert, .sound, .badge]) { [weak self] granted, _ in
            DispatchQueue.main.async {
                self?.permissionGranted = granted
            }
        }
    }

    func enableReminder() {
        let content = UNMutableNotificationContent()
        content.title = "该起来活动啦"
        content.body = "已经坐了20分钟，站起来走动一下，放松颈肩和腰背。"
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 20 * 60, repeats: true)
        let request = UNNotificationRequest(identifier: reminderId, content: content, trigger: trigger)

        center.add(request) { [weak self] error in
            DispatchQueue.main.async {
                self?.reminderEnabled = (error == nil)
            }
        }
    }

    func disableReminder() {
        center.removePendingNotificationRequests(withIdentifiers: [reminderId])
        DispatchQueue.main.async {
            self.reminderEnabled = false
        }
    }
}

private extension UNUserNotificationCenter {
    func notificationSettings() async -> UNNotificationSettings {
        await withCheckedContinuation { continuation in
            getNotificationSettings { settings in
                continuation.resume(returning: settings)
            }
        }
    }
}
