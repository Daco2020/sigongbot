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

    is_thread = _is_thread_message(body)

    # 문의 채널에 메시지 남길 시 관리자 채널에 알림 유저 이름을 알림으로 준다.
    if (
        body["event"]["channel"] == settings.SUPPORT_CHANNEL
        and body["event"]["type"] == "message"
        and not body["event"].get("subtype")
        and not is_thread
    ):
        await client.chat_postMessage(
            channel=settings.ADMIN_CHANNEL,
            text=f"👋 <@{body['event']['user']}> 님이 <#{settings.SUPPORT_CHANNEL}> 에 문의를 남겼어요. 👀 <@{settings.ADMIN_IDS[0]}> <@{settings.ADMIN_IDS[1]}>",
        )


def _is_thread_message(body: MessageBodyType) -> bool:
    """
    메시지가 스레드에 속한 메시지인지 여부를 반환합니다.
    """
    event = body.get("event", {})
    thread_ts = event.get("message", {}).get("thread_ts")  # type: ignore
    ts = event.get("message", {}).get("ts")  # type: ignore
    is_thread = thread_ts != ts if thread_ts else False
    return is_thread
