import httpx
from config import settings
from schemas import SMSResponse
import logging

logger = logging.getLogger(__name__)


class MSGOvrxService:
    def __init__(self):
        self.api_key = settings.MSG_OVRX_API_KEY
        self.base_url = settings.MSG_OVRX_BASE_URL
        self.sender = settings.SMS_SENDER_NAME

    async def send_sms(self, to: str, message: str) -> SMSResponse:
        """Отправка SMS через MSG OVRX API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/core/api/sms/send",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "to": to,
                        "message": message,
                        "from": self.sender,
                        "channel": "sms"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return SMSResponse(
                        success=True,
                        message="SMS отправлено",
                        message_id=data.get("message_id")
                    )
                else:
                    logger.error(f"MSG OVRX API error: {response.text}")
                    return SMSResponse(
                        success=False,
                        message="Ошибка отправки SMS"
                    )

        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return SMSResponse(
                success=False,
                message="Ошибка подключения к SMS сервису"
            )


msg_ovrx_service = MSGOvrxService()