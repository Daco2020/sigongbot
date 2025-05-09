from datetime import datetime, timedelta
import asyncio
from app.config import settings
from loguru import logger
from typing import Any

from app.database.pomodoro import fetch_active_pomodoros, update_pomodoro_status
from app.slack.events.view_pomodoro_submit import generate_guide_message
from slack_sdk.web.async_client import AsyncWebClient

from app.utils import get_persona_profile


class PomodoroScheduler:
    def __init__(self, client: AsyncWebClient):
        self.client = client
        self.active_tasks: dict[int, asyncio.Task] = {}  # 활성 태스크 추적

    async def start(self):
        """뽀모도로 스케줄러를 시작합니다."""
        logger.info("뽀모도로 스케줄러 루프 시작")
        while True:
            try:
                # 활성 뽀모도로 세션 조회
                active_pomodoros = await fetch_active_pomodoros()
                logger.info(f"활성 뽀모도로 세션 조회: {len(active_pomodoros)}개")

                # 현재 처리 중인 세션 목록 업데이트
                current_pomodoro_ids = {p["id"] for p in active_pomodoros}

                # 종료된 태스크 정리
                completed_tasks = []
                for pomodoro_id, task in self.active_tasks.items():
                    if task.done():
                        completed_tasks.append(pomodoro_id)
                    elif pomodoro_id not in current_pomodoro_ids:
                        # DB에서 제거되었으나 태스크가 아직 실행 중인 경우
                        logger.info(f"비활성화된 뽀모도로 태스크 취소: {pomodoro_id}")
                        task.cancel()
                        completed_tasks.append(pomodoro_id)

                # 완료된 태스크 정리
                for pomodoro_id in completed_tasks:
                    self.active_tasks.pop(pomodoro_id, None)

                # 새로운 뽀모도로 세션 처리
                for pomodoro in active_pomodoros:
                    pomodoro_id = pomodoro["id"]

                    # 이미 처리 중인 세션은 건너뜀
                    if (
                        pomodoro_id in self.active_tasks
                        and not self.active_tasks[pomodoro_id].done()
                    ):
                        continue

                    # 새로운 세션 처리
                    # 참고: main.py에서 start_pomodoro_scheduler()에 create_task를 적용하므로
                    # 여기서 process_pomodoro에 추가로 create_task를 적용하는 것은
                    # 이중 비동기 태스크가 아니라 독립적인 자식 태스크를 생성하는 것입니다.
                    logger.info(f"새 뽀모도로 세션 처리 시작: ID {pomodoro_id}")
                    self.active_tasks[pomodoro_id] = asyncio.create_task(
                        self.process_pomodoro(pomodoro)
                    )

            except Exception as e:
                logger.error(f"뽀모도로 스케줄러 에러: {str(e)}")

            # 주기적으로 확인
            await asyncio.sleep(30)

    async def process_pomodoro(self, pomodoro: dict[str, Any]):
        """개별 뽀모도로 세션을 처리합니다."""
        try:
            pomodoro_id = pomodoro["id"]
            duration_type = pomodoro["duration_type"]
            total_sessions = pomodoro["sessions"]
            current_session = pomodoro["current_session"]
            guide_persona = pomodoro["guide_persona"]
            slack_ts = pomodoro["slack_ts"]
            slack_channel = settings.POMODORO_CHANNEL_ID

            # 페르소나 프로필 정보 가져오기
            persona_profile = get_persona_profile(guide_persona)

            # 작업/휴식 시간 계산
            if duration_type == "25_5":
                work_minutes = 25  # 실제 사용 시에는 25분으로 설정
                break_minutes = 5  # 실제 사용 시에는 5분으로 설정
            else:  # 50_10
                work_minutes = 50  # 실제 사용 시에는 50분으로 설정
                break_minutes = 10  # 실제 사용 시에는 10분으로 설정

            # 테스트 모드에서는 더 짧은 시간으로 설정
            if settings.ENV == "dev":
                work_minutes = 1  # 개발 환경에서는 1분으로 설정
                break_minutes = 1  # 개발 환경에서는 1분으로 설정

            # 작업 시간 대기
            await asyncio.sleep(work_minutes * 60)

            # 참여자 목록 가져오기
            participants = pomodoro["participants"]

            # 작업 완료, 휴식 시간 안내
            break_end_time = datetime.now() + timedelta(minutes=break_minutes)

            break_message = generate_guide_message(
                guide_persona=guide_persona,
                session_num=current_session,
                total_sessions=total_sessions,
                is_start=False,
                is_break=True,
                participants=participants,
                break_end_time=break_end_time,
            )

            # 페르소나에 맞는 프로필로 메시지 전송
            await self.client.chat_postMessage(
                channel=slack_channel,
                thread_ts=slack_ts,
                text=break_message,
                username=persona_profile["username"],
                icon_url=persona_profile["icon_url"],
            )

            # 휴식 시간 대기
            await asyncio.sleep(break_minutes * 60)

            # 현재 세션 업데이트
            next_session = current_session + 1

            # 모든 세션 완료 여부 확인
            if next_session > total_sessions:
                # 모든 세션 완료
                complete_message = generate_guide_message(
                    guide_persona=guide_persona,
                    session_num=current_session,
                    total_sessions=total_sessions,
                    is_start=False,
                    is_break=False,
                    is_complete=True,
                    participants=participants,
                )

                # 페르소나에 맞는 프로필로 메시지 전송
                await self.client.chat_postMessage(
                    channel=slack_channel,
                    thread_ts=slack_ts,
                    text=complete_message,
                    username=persona_profile["username"],
                    icon_url=persona_profile["icon_url"],
                )

                # 상태 업데이트
                await update_pomodoro_status(pomodoro_id, "completed", current_session)

            else:
                # 다음 세션 시작
                next_work_end_time = datetime.now() + timedelta(minutes=work_minutes)

                next_session_message = generate_guide_message(
                    guide_persona=guide_persona,
                    session_num=next_session,
                    total_sessions=total_sessions,
                    is_start=True,
                    participants=participants,
                    work_end_time=next_work_end_time,
                )

                # 페르소나에 맞는 프로필로 메시지 전송
                await self.client.chat_postMessage(
                    channel=slack_channel,
                    thread_ts=slack_ts,
                    text=next_session_message,
                    username=persona_profile["username"],
                    icon_url=persona_profile["icon_url"],
                )

                # 세션 업데이트
                updated_pomodoro = await update_pomodoro_status(
                    pomodoro_id, "in_progress", next_session
                )

                # 재귀적으로 다음 세션 처리
                await self.process_pomodoro(updated_pomodoro)

        except Exception as e:
            logger.error(
                f"뽀모도로 세션 처리 실패 - ID: {pomodoro.get('id', 'Unknown')}, Error: {str(e)}"
            )

            # 에러가 발생해도 상태 업데이트
            if "id" in pomodoro:
                await update_pomodoro_status(pomodoro["id"], "error")


async def start_pomodoro_scheduler(client: AsyncWebClient):
    """스케줄러를 시작하는 함수"""
    scheduler = PomodoroScheduler(client)
    await scheduler.start()
