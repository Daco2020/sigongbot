from app.slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    InputBlock,
    PlainTextInputElement,
    NumberInputElement,
    SectionBlock,
)

from app.utils import format_remaining_time, get_current_session_info


async def handle_command_retrospective(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """회고 제출 명령어 처리"""
    await ack()

    current_session_info = get_current_session_info()
    session_name = current_session_info[1]
    remaining_time = current_session_info[2]
    remaining_time_str = format_remaining_time(remaining_time)

    # TODO: 해당 유저가 이미 공유 했다면 모달 안내창 띄우기

    # 블록 생성
    blocks = [
        SectionBlock(
            text=f"이번 회고 공유 회차는 `{session_name}` 입니다.\n공유 마감까지 남은 시간은 `{remaining_time_str}`입니다.",
        ),
        InputBlock(
            block_id="good_points",
            label="잘했고 좋았던 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="good_points_input",
                multiline=True,
            ),
        ),
        InputBlock(
            block_id="improvements",
            label="아쉽고 개선하고 싶은 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="improvements_input",
                multiline=True,
            ),
        ),
        InputBlock(
            block_id="learnings",
            label="새롭게 배운 점을 알려주세요",
            element=PlainTextInputElement(
                action_id="learnings_input",
                multiline=True,
            ),
        ),
        InputBlock(
            block_id="action_item",
            label="해볼만한 액션 아이템을 알려주세요",
            element=PlainTextInputElement(
                action_id="action_item_input",
                multiline=True,
            ),
        ),
        InputBlock(
            optional=True,
            block_id="emotion_score",
            label="오늘의 감정점수를 알려주세요 (1-10)",
            element=NumberInputElement(
                action_id="emotion_score_input",
                is_decimal_allowed=False,
                min_value="1",
                max_value="10",
            ),
        ),
        InputBlock(
            optional=True,
            block_id="emotion_reason",
            label="감정점수 이유를 알려주세요",
            element=PlainTextInputElement(
                action_id="emotion_reason_input",
                multiline=True,
            ),
        ),
    ]

    # 명령어가 실행된 채널 ID 저장
    channel_id = body["channel_id"]

    # 모달 뷰 생성
    view = View(
        type="modal",
        callback_id="retrospective_submit",
        title="회고 공유",
        submit="공유하기",
        blocks=blocks,
        private_metadata=channel_id,  # 채널 ID를 private_metadata에 저장
    )

    # 모달 열기
    await client.views_open(trigger_id=body["trigger_id"], view=view)
