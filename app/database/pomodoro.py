from app.database.supabase import supabase
from loguru import logger
from typing import Any


async def create_pomodoro(
    user_id: str,
    duration_type: str,
    sessions: int,
    guide_persona: str,
    participants: list[str],
    slack_ts: str,
) -> dict[str, Any]:
    """뽀모도로 세션을 생성합니다."""
    try:
        # 뽀모도로 데이터 생성
        response = (
            await supabase.table("pomodoros")
            .insert(
                {
                    "user_id": user_id,
                    "duration_type": duration_type,
                    "sessions": sessions,
                    "guide_persona": guide_persona,
                    "participants": participants,
                    "slack_ts": slack_ts,
                    "status": "in_progress",
                    "current_session": 1,
                }
            )
            .execute()
        )

        if len(response.data) == 0:
            raise Exception("Failed to create pomodoro record")

        return response.data[0]
    except Exception as e:
        logger.error(f"뽀모도로 생성 실패: {str(e)}")
        raise e


async def update_pomodoro_status(
    pomodoro_id: int,
    status: str,
    current_session: int | None = None,
) -> dict[str, Any]:
    """뽀모도로 상태를 업데이트합니다."""
    try:
        update_data: dict[str, Any] = {"status": status}
        if current_session is not None:
            update_data["current_session"] = current_session

        response = (
            await supabase.table("pomodoros")
            .update(update_data)
            .eq("id", pomodoro_id)
            .execute()
        )

        if len(response.data) == 0:
            raise Exception(f"Failed to update pomodoro {pomodoro_id}")

        return response.data[0]
    except Exception as e:
        logger.error(f"뽀모도로 상태 업데이트 실패: {str(e)}")
        raise e


async def fetch_active_pomodoros() -> list[dict[str, Any]]:
    """진행 중인 뽀모도로 세션을 조회합니다."""
    try:
        response = (
            await supabase.table("pomodoros")
            .select("*")
            .eq("status", "in_progress")
            .execute()
        )

        return response.data
    except Exception as e:
        logger.error(f"진행 중인 뽀모도로 조회 실패: {str(e)}")
        raise e


async def get_pomodoro_by_id(pomodoro_id: int) -> dict[str, Any] | None:
    """ID로 뽀모도로 세션을 조회합니다."""
    try:
        response = (
            await supabase.table("pomodoros")
            .select("*")
            .eq("id", pomodoro_id)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]
    except Exception as e:
        logger.error(f"뽀모도로 조회 실패 - ID: {pomodoro_id}, Error: {str(e)}")
        raise e
