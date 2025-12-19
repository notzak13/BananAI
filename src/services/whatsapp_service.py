from twilio.rest import Client


class WhatsAppService:
    """
    Sends WhatsApp messages using Twilio API.
    """

    def __init__(self, sid: str, token: str, from_number: str, to_number: str):
        self.client = Client(sid, token)
        self.from_number = from_number
        self.to_number = to_number

    def send(self, message: str) -> str:
        msg = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=self.to_number
        )
        return msg.sid
