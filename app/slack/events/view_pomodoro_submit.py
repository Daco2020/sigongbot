from datetime import datetime, timedelta
from loguru import logger
from app.slack.types import ViewBodyType, ViewType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import (
    SectionBlock,
    ContextBlock,
)

from app.database.pomodoro import create_pomodoro
from app.slack.events.command_pomodoro import calculate_total_time
from app.config import settings
from app.utils import get_persona_profile


async def handle_view_pomodoro_submit(
    ack: AsyncAck, body: ViewBodyType, client: AsyncWebClient, view: ViewType
):
    """뽀모도로 설정 모달 제출 처리"""
    await ack()

    user_id = body["user"]["id"]
    pomodoro_channel_id = settings.POMODORO_CHANNEL_ID

    # 모달에서 입력된 값 추출
    values = view["state"]["values"]

    # 유형 선택
    duration_type = values["duration_type"]["duration_type_select"]["selected_option"][
        "value"
    ]

    # 작업/휴식 시간 계산
    if duration_type == "25_5":
        work_minutes = 25
        break_minutes = 5
        duration_text = "25분 작업 + 5분 휴식"
    else:  # 50_10
        work_minutes = 50
        break_minutes = 10
        duration_text = "50분 작업 + 10분 휴식"

    # 테스트 모드에서는 더 짧은 시간으로 설정
    if settings.ENV == "dev":
        work_minutes = 1  # 개발 환경에서는 1분으로 설정
        break_minutes = 1  # 개발 환경에서는 1분으로 설정

    # 세션 수
    sessions = int(values["sessions"]["sessions_select"]["selected_option"]["value"])

    # 가이드 페르소나
    guide_persona = values["guide_persona"]["guide_persona_select"]["selected_option"][
        "value"
    ]
    guide_text = values["guide_persona"]["guide_persona_select"]["selected_option"][
        "text"
    ]["text"]

    # 페르소나 프로필 정보 가져오기
    persona_profile = get_persona_profile(guide_persona)

    # 참가자 (선택 사항)
    participants = []
    if "participants" in values and values["participants"]["participants_select"].get(
        "selected_users"
    ):
        participants = values["participants"]["participants_select"]["selected_users"]

    # 참가자에 자기 자신 추가
    if user_id not in participants:
        participants.append(user_id)

    try:
        # 참가자 멘션 생성
        participants_mention = " ".join([f"<@{p}>" for p in participants])

        # 현재 시간 기준으로 첫 번째 작업 시간 계산
        now = datetime.now()
        work_end_time = now + timedelta(minutes=work_minutes)
        break_end_time = work_end_time + timedelta(minutes=break_minutes)
        # 시작 메시지 생성
        message_blocks = [
            SectionBlock(text="🍅 *뽀모도로 세션이 시작되었습니다!* 🍅"),
            SectionBlock(
                text=f"• *세션:* {duration_text}\n• *총 횟수:* {sessions}회 ({calculate_total_time(sessions, duration_type)})\n• *가이드:* {guide_text}"
            ),
            SectionBlock(text=f"*참가자:* {participants_mention}"),
            ContextBlock(
                elements=[
                    {
                        "type": "mrkdwn",
                        "text": "이 스레드에서 뽀모도로 진행 상황을 확인하세요.",
                    }
                ]
            ),
        ]

        # 메시지 전송
        message_response = await client.chat_postMessage(
            channel=pomodoro_channel_id,
            blocks=message_blocks,
            text="뽀모도로 세션이 시작되었습니다! 🍅",
        )

        # 메시지 저장
        slack_ts = message_response["ts"]

        # 첫 번째 뽀모도로 안내 메시지 생성 (스레드 답글)
        guide_message = generate_guide_message(
            guide_persona=guide_persona,
            session_num=1,
            total_sessions=sessions,
            is_start=True,
            work_end_time=work_end_time,
            break_end_time=break_end_time,
        )

        await client.chat_postMessage(
            channel=pomodoro_channel_id,
            thread_ts=slack_ts,
            text=guide_message,
            username=persona_profile["username"],
            icon_url=persona_profile["icon_url"],
        )

        # 데이터베이스에 뽀모도로 세션 저장
        await create_pomodoro(
            user_id=user_id,
            duration_type=duration_type,
            sessions=sessions,
            guide_persona=guide_persona,
            participants=participants,
            slack_ts=slack_ts,
        )

    except Exception as e:
        logger.error(f"뽀모도로 세션 생성 실패 - User: {user_id}, Error: {str(e)}")
        await ack(response_action="errors", errors={"sessions": f"오류 발생: {str(e)}"})


def generate_guide_message(
    guide_persona: str,
    session_num: int,
    total_sessions: int,
    is_start: bool,
    work_end_time: datetime | None = None,
    is_break: bool = False,
    break_end_time: datetime | None = None,
    is_complete: bool = False,
) -> str:
    """가이드 유형에 따른 메시지를 생성합니다."""
    # 시간 형식 변환
    time_format = "%H:%M"

    if is_complete:
        # 세션 완료 메시지
        if guide_persona == "strict_female_boss":
            return "모든 뽀모도로 세션이 완료되었습니다. 오늘 업무 잘 하셨네요. 내일도 이 페이스를 유지하세요."
        elif guide_persona == "sweet_male_mentor":
            return "여러분! 오늘의 뽀모도로를 모두 완료했습니다. 정말 잘 하셨어요! 오늘처럼 집중해서 좋은 결과가 있길 바랍니다."
        elif guide_persona == "cheerful_female_junior":
            return "와~ 우리 모든 세션 끝났다! 너무 잘했어! 오늘 진짜 대단한데? 다음에도 같이 해요~~ 🎉"
        else:  # rival_male_friend
            return "음, 생각보다 빨리 끝났네. 나는 좀 더 집중했을 것 같은데... 다음에는 더 높은 목표로 도전해볼까?"

    if is_start:
        # 작업 시작 메시지
        work_end_str = work_end_time.strftime(time_format) if work_end_time else ""

        if guide_persona == "strict_female_boss":
            return f"{session_num}번째 작업을 시작합니다. {work_end_str}까지 집중해서 작업해주세요. 중간에 딴짓하지 마세요."
        elif guide_persona == "sweet_male_mentor":
            return f"{session_num}번째 작업 시간입니다! {work_end_str}까지 집중해보세요. 여러분의 노력이 좋은 결실을 맺을 거예요."
        elif guide_persona == "cheerful_female_junior":
            return f"{session_num}번째 시작! {work_end_str}까지 같이 열심히 해보자~! 화이팅이야! ✨"
        else:  # rival_male_friend
            return f"{session_num}번째 시작. 난 이미 시작했는데... 너도 {work_end_str}까지 얼마나 집중할 수 있는지 볼게."

    if is_break and break_end_time:
        # 휴식 안내 메시지
        break_end_str = break_end_time.strftime(time_format)

        if guide_persona == "strict_female_boss":
            return f"{session_num}번째 작업이 끝났습니다. {break_end_str}까지 휴식 시간입니다. 정확히 시간을 지켜주세요."
        elif guide_persona == "sweet_male_mentor":
            return f"잘하셨어요! {session_num}번째 작업을 완료했습니다. {break_end_str}까지 휴식을 취하세요. 충분한 휴식도 중요합니다."
        elif guide_persona == "cheerful_female_junior":
            return f"우와~ {session_num}번째 끝났다! {break_end_str}까지 쉬는 시간이야! 간식이라도 먹자~ 🍪"
        else:  # rival_male_friend
            return f"{session_num}번째 끝. 휴식은 {break_end_str}까지. 내가 더 효율적으로 시간을 쓰고 있는 것 같은데?"

    # 기본 메시지
    return f"{session_num}/{total_sessions} 뽀모도로 진행 중"
