import datetime
from app.utils import get_current_session_info, format_remaining_time
from app.constants import (
    DUE_DATES,
    SESSION_NAMES,
)  # DUE_DATES와 SESSION_NAMES를 import 해야 합니다


def test_get_current_session_info():
    # 시작 전 케이스
    start_time = DUE_DATES[0] - datetime.timedelta(days=1)
    idx, name, remaining, is_active = get_current_session_info(start_time)
    assert idx == 0
    assert name == SESSION_NAMES[0]
    assert isinstance(remaining, datetime.timedelta)
    assert is_active is True

    # 진행 중인 케이스
    middle_time = DUE_DATES[0] + datetime.timedelta(hours=1)
    idx, name, remaining, is_active = get_current_session_info(middle_time)
    assert idx == 1
    assert name == SESSION_NAMES[1]
    assert isinstance(remaining, datetime.timedelta)
    assert is_active is True

    # 모든 회차가 끝난 케이스
    end_time = DUE_DATES[-1] + datetime.timedelta(days=1)
    idx, name, remaining, is_active = get_current_session_info(end_time)
    assert idx == len(DUE_DATES) - 1
    assert name == SESSION_NAMES[-1]
    assert remaining == datetime.timedelta(0)
    assert is_active is False


def test_format_remaining_time():
    # 일/시간/분이 모두 있는 경우
    td = datetime.timedelta(days=2, hours=3, minutes=30)
    assert format_remaining_time(td) == "2일 3시간 30분"

    # 시간/분만 있는 경우
    td = datetime.timedelta(hours=5, minutes=45)
    assert format_remaining_time(td) == "5시간 45분"

    # 분만 있는 경우
    td = datetime.timedelta(minutes=20)
    assert format_remaining_time(td) == "20분"

    # 0인 경우
    td = datetime.timedelta(0)
    assert format_remaining_time(td) == "0분"


def test_get_current_session_info_edge_cases():
    # 정확히 마감시간인 경우
    exact_due = DUE_DATES[0]
    idx, name, remaining, is_active = get_current_session_info(exact_due)
    assert idx == 1
    assert name == SESSION_NAMES[1]
    assert isinstance(remaining, datetime.timedelta)
    assert is_active is True


def test_format_remaining_time_edge_cases():
    # 59분인 경우
    td = datetime.timedelta(minutes=59)
    assert format_remaining_time(td) == "59분"

    # 23시간 59분인 경우
    td = datetime.timedelta(hours=23, minutes=59)
    assert format_remaining_time(td) == "23시간 59분"
