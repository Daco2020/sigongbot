from app.slack.types import MessageBodyType
from app.config import settings

from slack_bolt.async_app import AsyncAck, AsyncSay
from slack_sdk.web.async_client import AsyncWebClient


async def handle_message(
    ack: AsyncAck,
    body: MessageBodyType,
    say: AsyncSay,
    client: AsyncWebClient,
) -> None:
    """메시지 이벤트 처리"""
    await ack()

    # 문의 채널에 메시지 남길 시 관리자 채널에 알림 유저 이름을 알림으로 준다.
    if (
        body["event"]["channel"] == settings.SUPPORT_CHANNEL
        and body["event"]["type"] == "message"
        and not body["event"].get("subtype")
    ):
        await client.chat_postMessage(
            channel=settings.ADMIN_CHANNEL,
            text=f"🤓 <@{body['event']['user']}> 님이 문의 채널에 메시지를 남겼습니다. \n```📋 문의 내용:\n\n{body['event']['text']}```\n🤗 문의 내용을 확인해주세요. <@{settings.ADMIN_IDS[0]}>, <@{settings.ADMIN_IDS[1]}>",
        )
