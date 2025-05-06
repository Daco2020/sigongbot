from app.slack.types import CommandBodyType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    SectionBlock,
    DividerBlock,
    InputBlock,
    StaticSelectElement,
    Option,
    UserMultiSelectElement,
)


async def handle_command_pomodoro(
    ack: AsyncAck, body: CommandBodyType, client: AsyncWebClient
):
    """뽀모도로 명령어 처리"""
    await ack()

    # 뽀모도로 설정 모달 생성
    blocks = [
        SectionBlock(
            text="뽀모도로 세션을 설정해주세요. 설정한 뽀모도로는 자동으로 시작됩니다."
        ),
        DividerBlock(),
        InputBlock(
            block_id="duration_type",
            label="🍅 뽀모도로 세션을 선택하세요",
            element=StaticSelectElement(
                action_id="duration_type_select",
                options=[
                    Option(
                        text="25분 작업 + 5분 휴식 (30분/세션)",
                        value="25_5",
                    ),
                    Option(
                        text="50분 작업 + 10분 휴식 (60분/세션)",
                        value="50_10",
                    ),
                ],
                initial_option=Option(
                    text="25분 작업 + 5분 휴식 (30분/세션)",
                    value="25_5",
                ),
            ),
        ),
        InputBlock(
            block_id="sessions",
            label="🔁 반복 횟수를 선택하세요",
            element=StaticSelectElement(
                action_id="sessions_select",
                options=[Option(text=f"{i}회", value=str(i)) for i in range(1, 13)],
                initial_option=Option(text="4회", value="4"),
            ),
        ),
        InputBlock(
            block_id="guide_persona",
            label="👩‍🏫 가이드 페르소나를 선택하세요",
            element=StaticSelectElement(
                action_id="guide_persona_select",
                options=[
                    Option(text="라이벌 동기", value="rival_male_friend"),
                    Option(text="해맑은 후배", value="cheerful_female_junior"),
                    Option(text="스윗한 멘토", value="sweet_male_mentor"),
                    Option(text="깐깐한 상사", value="strict_female_boss"),
                ],
                initial_option=Option(text="라이벌 동기", value="rival_male_friend"),
            ),
        ),
        InputBlock(
            block_id="participants",
            label="😘 함께할 참가자를 선택하세요",
            element=UserMultiSelectElement(
                action_id="participants_select",
                initial_users=[body["user_id"]],
            ),
        ),
    ]

    # 모달 뷰 생성
    view = View(
        type="modal",
        callback_id="pomodoro_submit",
        title="뽀모도로 설정",
        submit="시작하기",
        blocks=blocks,
    )

    # 모달 열기
    await client.views_open(trigger_id=body["trigger_id"], view=view)


def calculate_total_time(sessions: int, duration_type: str) -> str:
    """총 소요 시간을 계산합니다."""
    if duration_type == "25_5":
        work_minutes = 25
        break_minutes = 5
    else:  # 50_10
        work_minutes = 50
        break_minutes = 10

    total_minutes = sessions * (work_minutes + break_minutes)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0:
        return f"{hours}시간 {minutes}분"
    else:
        return f"{minutes}분"
