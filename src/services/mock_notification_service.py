from src.services.notification_service import NotificationService

class MockNotificationService(NotificationService):
    def send(self, message: str):
        print("\n[MOCK NOTIFICATION]")
        print(message)
        print("[END MOCK]\n")
        return "MOCK-SENT"