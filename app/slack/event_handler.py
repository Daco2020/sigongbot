import re
import traceback
from typing import Callable
from app.config import settings
from slack_bolt.async_app import AsyncApp as SlackBoltAsyncApp

from loguru import logger
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk.models.blocks import SectionBlock
from slack_sdk.models.views import View

from app.exception import BotException
from app.slack.events.command_retrospective import handle_command_retrospective
from app.slack.events.command_admin import handle_command_admin
from app.slack.events.message import handle_message
from app.slack.events.view_retrospective_submit import handle_view_retrospective_submit
from app.slack.events.view_admin_menu import (
    handle_view_admin_menu,
    handle_admin_action_delete,
    handle_admin_action_edit,
    handle_view_admin_delete_retrospective,
    handle_view_admin_edit_retrospective,
)


app = SlackBoltAsyncApp()


@app.middleware
async def log_event_middleware(
    req: BoltRequest,
    resp: BoltResponse,
    next: Callable,
) -> None:
    """이벤트 로깅 미들웨어"""
    logger.info(f"Received event: {req.body}")
    await next()


@app.error
async def handle_error(error, body):
    """이벤트 핸들러에서 발생한 에러 처리"""
    logger.error(f'"{str(error)}"')
    trace = traceback.format_exc()
    logger.debug(dict(body=body, error=trace))

    # 사용자에게 에러를 알립니다.
    if re.search(r"[\u3131-\uD79D]", str(error)):
        # 한글로 핸들링하는 메시지만 사용자에게 전송합니다.
        message = str(error)
    else:
        message = "예기치 못한 오류가 발생했어요."

    text = f"🥲 {message}\n\n👉🏼 문제가 해결되지 않는다면 <#{settings.SUPPORT_CHANNEL}> 채널로 문의해주세요."
    if trigger_id := body.get("trigger_id"):
        await app.client.views_open(
            trigger_id=trigger_id,
            view=View(
                type="modal",
                title={"type": "plain_text", "text": "잠깐!"},
                blocks=[SectionBlock(text=text)],
            ),
        )

    # 관리자에게 에러를 알립니다.
    if isinstance(error, BotException):
        await app.client.chat_postMessage(
            channel=settings.ADMIN_CHANNEL,
            text=f"🫢: {error=} 🕊️: {trace=} 👉🏼 💌: {body=}",
        )
    else:
        await app.client.chat_postMessage(
            channel=settings.ADMIN_CHANNEL,
            text=f"⛈️ 핸들링이 필요한 에러입니다. 🫢: {error=} 🕊️: {trace=} 👉🏼 💌: {body=}",
        )


# message
app.event("message")(handle_message)

# retrospective
app.command("/공유")(handle_command_retrospective)
app.view("retrospective_submit")(handle_view_retrospective_submit)

# admin
app.command("/관리자")(handle_command_admin)  # 관리자 메뉴 호출
app.view("admin_menu")(handle_view_admin_menu)  # 관리자 메뉴 출력
app.view("admin_edit_retrospective")(
    handle_view_admin_edit_retrospective
)  # 회고 수정 제출 처리
app.view("admin_delete_retrospective")(
    handle_view_admin_delete_retrospective
)  # 회고 삭제 모달 처리

# 회고 관리 액션
app.action("edit_retrospective")(handle_admin_action_edit)  # 회고 수정 버튼
app.action("delete_retrospective")(handle_admin_action_delete)  # 회고 삭제 버튼
