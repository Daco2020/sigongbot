import random
import string
from typing import Any, Tuple
import orjson
import regex as re
import datetime

from zoneinfo import ZoneInfo

from app.constants import DUE_DATES, SESSION_NAMES


def tz_now(tz: str = "Asia/Seoul") -> datetime.datetime:
    """현재시간 반환합니다."""
    return datetime.datetime.now(tz=ZoneInfo(tz))


def tz_now_to_str(tz: str = "Asia/Seoul") -> str:
    """현재시간을 문자열로 반환합니다."""
    return datetime.datetime.strftime(tz_now(tz), "%Y-%m-%d %H:%M:%S")


def generate_unique_id() -> str:
    """고유한 ID를 생성합니다."""
    # 무작위 문자열 6자리 + 밀리 세컨즈(문자로 치환된)
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{random_str}{str(int(datetime.datetime.now().timestamp() * 1000))}"


def remove_emoji(message: str) -> str:
    """이모지를 제거합니다."""
    emoji_code_pattern = re.compile(r":[a-zA-Z0-9_\-]+:|:\p{Script=Hangul}+:")
    return emoji_code_pattern.sub(r"", message)


def slack_link_to_markdown(text):
    """Slack 링크를 마크다운 링크로 변환합니다."""
    pattern = re.compile(r"<(http[s]?://[^\|]+)\|([^\>]+)>")
    return pattern.sub(r"[\2](\1)", text)


def dict_to_json_str(data: dict[str, Any]) -> str:
    """dict를 json string으로 변환합니다."""
    return orjson.dumps(data).decode("utf-8")


def json_str_to_dict(data: str) -> dict[str, Any]:
    """json string을 dict로 변환합니다."""
    return orjson.loads(data)


def ts_to_dt(ts: str) -> datetime.datetime:
    """timestamp를 datetime으로 변환합니다."""
    return datetime.datetime.fromtimestamp(float(ts))


def get_current_session_info(
    current_time: datetime.datetime | None = None,
) -> Tuple[int, str, datetime.timedelta, bool]:
    """
    현재 날짜 기준 회차 정보와 마감까지 남은 시간을 반환합니다.

    Args:
        current_time: 현재 시간 (기본값: 현재 시간)

    Returns:
        Tuple[회차 인덱스, 회차 이름, 남은 시간, 마감 여부]
        - session_idx(회차 인덱스): 0부터 시작하는 회차 인덱스
        - session_name(회차 이름): 회차 설명 (예: "1회차")
        - remaining_time(남은 시간): 마감까지 남은 시간 (timedelta)
        - is_active(활성 여부): 커뮤니티 활성화 여부 (True/False)
    """
    if current_time is None:
        current_time = datetime.datetime.now()

    # 모든 마감이 완료된 경우
    if current_time >= DUE_DATES[-1]:
        last_idx = len(DUE_DATES) - 1
        return last_idx, SESSION_NAMES[last_idx], datetime.timedelta(0), False

    # 시작 전인 경우
    if current_time < DUE_DATES[0]:
        return 0, SESSION_NAMES[0], DUE_DATES[0] - current_time, True

    # 현재 회차 찾기
    for i in range(len(DUE_DATES) - 1):
        if DUE_DATES[i] <= current_time < DUE_DATES[i + 1]:
            next_due = DUE_DATES[i + 1]
            remaining = next_due - current_time
            return i + 1, SESSION_NAMES[i + 1], remaining, True

    raise ValueError("현재 회차를 찾을 수 없습니다.")


def format_remaining_time(remaining: datetime.timedelta) -> str:
    """
    남은 시간을 읽기 쉬운 형식으로 변환합니다.

    Args:
        remaining: 남은 시간 (timedelta)

    Returns:
        읽기 쉬운 형식의 남은 시간
    """
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60

    if days > 0:
        return f"{days}일 {hours}시간 {minutes}분"
    elif hours > 0:
        return f"{hours}시간 {minutes}분"
    else:
        return f"{minutes}분"
