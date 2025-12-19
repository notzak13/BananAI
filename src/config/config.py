import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
    WHATSAPP_TO = os.getenv("TWILIO_WHATSAPP_TO")

    @staticmethod
    def whatsapp_enabled() -> bool:
        enabled = all([
            Config.TWILIO_ACCOUNT_SID,
            Config.TWILIO_AUTH_TOKEN,
            Config.WHATSAPP_FROM,
            Config.WHATSAPP_TO
        ])
        print("WHATSAPP ENABLED:", enabled)
        return enabled
