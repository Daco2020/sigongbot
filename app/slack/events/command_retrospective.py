from app.slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    InputBlock,
    PlainTextInputElement,
    NumberInputElement,
)


async def handle_command_retrospective(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """회고 제출 명령어 처리"""
    await ack()

    # 블록 생성
    blocks = [
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

    # 모달 뷰 생성
    view = View(
        type="modal",
        callback_id="retrospective_submit",
        title="회고 공유",
        submit="공유하기",
        blocks=blocks,
    )

    # 모달 열기
    await client.views_open(trigger_id=body["trigger_id"], view=view)
