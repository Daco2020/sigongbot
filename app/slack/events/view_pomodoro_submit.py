from datetime import datetime, timedelta
from loguru import logger
from app.slack.types import ViewBodyType, ViewType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import (
    SectionBlock,
    ContextBlock,
)
from zoneinfo import ZoneInfo

from app.database.pomodoro import create_pomodoro
from app.slack.events.command_pomodoro import calculate_total_time
from app.config import settings
from app.utils import get_persona_profile, tz_now


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
        work_end_time = tz_now() + timedelta(minutes=work_minutes)
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
            participants=participants,
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
    participants: list[str],
    work_end_time: datetime | None = None,
    is_break: bool = False,
    break_end_time: datetime | None = None,
    is_complete: bool = False,
) -> str:
    """가이드 유형에 따른 메시지를 생성합니다."""
    # 시간 형식 변환
    time_format = "%H:%M"
    participants_mention = " ".join([f"<@{p}>" for p in participants])

    # UTC를 KST로 변환
    if work_end_time:
        work_end_time = work_end_time.astimezone(ZoneInfo("Asia/Seoul"))
    if break_end_time:
        break_end_time = break_end_time.astimezone(ZoneInfo("Asia/Seoul"))

    if is_complete:
        # 세션 완료 메시지
        if guide_persona == "strict_female_boss":
            message = "모든 뽀모도로 세션이 끝났어. 흥, 오늘 꽤 잘 했네. 내일도 이 페이스를 유지하라고. 자 잠깐!! 벌써 가려고..? 오늘 나랑 같이 한 소감은 말해줘야지!"
        elif guide_persona == "sweet_male_mentor":
            message = "여러분! 오늘의 뽀모도로를 모두 완료했습니다. 정말 잘 하셨어요! 오늘처럼 집중하면 무엇이든 이룰 수 있답니다. ☺️ 오늘 뽀모도로 소감도 남겨보세요."
        elif guide_persona == "cheerful_female_junior":
            message = "와~ 우리 모든 세션 끝났다! 🎉 오늘 다들 대단한데요? 다음에도 나랑 같이 해줄거죠오~~!? ✨ 아 맞다! 뽀모도로 후기 남기는 것도 잊지말아요~!"
        else:  # rival_male_friend
            message = "음, 생각보다 빨리 끝났네? 나는 좀 더 할 수 있을 것 같은데ㅎ 다음에는 더 오래 하면 좋을 듯. 그리고 뽀모도로 회고는 필수인거 알지?"
        return f"{participants_mention}\n\n{message}"

    if is_start:
        # 작업 시작 메시지
        work_end_str = work_end_time.strftime(time_format) if work_end_time else ""

        if guide_persona == "strict_female_boss":
            message = f"{session_num}번째 작업 시작할거야. {work_end_str}까지 집중해서 작업해. 중간에 한 눈 팔지 말고."
        elif guide_persona == "sweet_male_mentor":
            message = f"{session_num}번째 작업 시간입니다! {work_end_str}까지 집중해보세요. 노력은 거짓말하지 않는답니다~"
        elif guide_persona == "cheerful_female_junior":
            message = f"{session_num}번째 시작! {work_end_str}까지 열심히 해보자구요~! 💪 우리 모두 화이팅구구! 🕊️"
        else:  # rival_male_friend
            message = f"{session_num}번째 시작. (사실 난 이미 시작했지만ㅎ) {work_end_str}까지 네가 얼마나 집중하는지 볼게."
        return f"{participants_mention}\n\n{message}"

    if is_break and break_end_time:
        # 휴식 안내 메시지
        break_end_str = break_end_time.strftime(time_format)

        if guide_persona == "strict_female_boss":
            message = f"{session_num}번째 작업이 끝났어. {break_end_str}까지 휴식 시간이야. 정확히 시간을 지키지 않으면 내가 곤란해."
        elif guide_persona == "sweet_male_mentor":
            message = f"잘하셨어요! {session_num}번째 작업을 완료했습니다. {break_end_str}까지 휴식을 취하세요. 충분한 휴식도 중요하답니다."
        elif guide_persona == "cheerful_female_junior":
            message = f"우와~ {session_num}번째 끝났다! {break_end_str}까지 쉬는 시간이에요! 간식이라도 먹을래요~? 🍪"
        else:  # rival_male_friend
            message = f"{session_num}번째 끝. 휴식은 {break_end_str}까지. 아 물론 나는 안 쉴거야. 난 쉬는게 더 피곤하거든ㅎ"
        return f"{participants_mention}\n\n{message}"

    # 기본 메시지
    return f"{session_num}/{total_sessions} 뽀모도로 진행 중"
