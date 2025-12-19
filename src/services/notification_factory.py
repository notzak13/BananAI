from src.config.config import Config
from src.services.whatsapp_service import WhatsAppService
from src.services.mock_notification_service import MockNotificationService

class NotificationFactory:

    @staticmethod
    def create():
        if Config.whatsapp_enabled():
            return WhatsAppService(
                Config.TWILIO_ACCOUNT_SID,
                Config.TWILIO_AUTH_TOKEN,
                Config.WHATSAPP_FROM,
                Config.WHATSAPP_TO
            )
        return MockNotificationService()
