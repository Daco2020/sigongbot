from loguru import logger
from app.slack.types import ViewBodyType, ViewType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient


async def handle_view_retrospective_submit(
    ack: AsyncAck, body: ViewBodyType, client: AsyncWebClient, view: ViewType
):
    """모달 제출 처리"""
    user_id = body["user"]["id"]

    try:
        # TODO: Supabase 연동 구현 필요
        await ack()
        await client.chat_postEphemeral(
            channel=body["user"]["id"],
            user=user_id,
            text="회고가 성공적으로 제출되었습니다! 🎉",
        )

        # 로깅 추가
        logger.info(f"회고 제출 완료 - User: {user_id}")

    except Exception as e:
        logger.error(f"회고 제출 실패 - User: {user_id}, Error: {str(e)}")
        await ack(
            response_action="errors",
            errors={
                "good_points": "데이터 저장 중 오류가 발생했습니다. 다시 시도해주세요."
            },
        )
