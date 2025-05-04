from loguru import logger
from app.slack.types import ViewBodyType, ViewType
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import SectionBlock, DividerBlock, ContextBlock

from app.utils import get_current_session_info


async def handle_view_retrospective_submit(
    ack: AsyncAck, body: ViewBodyType, client: AsyncWebClient, view: ViewType
):
    """모달 제출 처리"""
    user_id = body["user"]["id"]

    try:
        # 모달에서 입력된 값 추출
        values = view["state"]["values"]

        # 각 필드의 입력값 추출
        good_points = (
            values["good_points"]["good_points_input"]["value"] or "작성되지 않음"
        )
        improvements = (
            values["improvements"]["improvements_input"]["value"] or "작성되지 않음"
        )
        learnings = values["learnings"]["learnings_input"]["value"] or "작성되지 않음"
        action_item = (
            values["action_item"]["action_item_input"]["value"] or "작성되지 않음"
        )

        # 선택적 필드 처리
        emotion_score = (
            values.get("emotion_score", {})
            .get("emotion_score_input", {})
            .get("value", "")
        )
        emotion_reason = (
            values.get("emotion_reason", {})
            .get("emotion_reason_input", {})
            .get("value", "")
        )

        current_session_info = get_current_session_info()
        session_name = current_session_info[1]

        # 메시지 블록 생성
        blocks = [
            SectionBlock(
                text=f"*<@{user_id}>님이 {session_name} 회고를 공유했어요! 🤗*"
            ),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*잘했고 좋았던 점* 🌟"}]
            ),
            SectionBlock(text=good_points),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*아쉽고 개선하고 싶은 점* 🔧"}]
            ),
            SectionBlock(text=improvements),
            DividerBlock(),
            ContextBlock(elements=[{"type": "mrkdwn", "text": "*새롭게 배운 점* 💡"}]),
            SectionBlock(text=learnings),
            DividerBlock(),
            ContextBlock(
                elements=[{"type": "mrkdwn", "text": "*해볼만한 액션 아이템* 🚀"}]
            ),
            SectionBlock(text=action_item),
        ]

        # 감정 점수가 입력되었다면 추가
        if emotion_score:
            blocks.extend(
                [
                    DividerBlock(),
                    SectionBlock(
                        text=f"*오늘의 감정점수* :bar_chart: {emotion_score}/10"
                    ),
                ]
            )

            # 감정 이유가 입력되었다면 추가
            if emotion_reason:
                blocks.append(SectionBlock(text=emotion_reason))

        # command_retrospective에서 호출된 채널 ID 가져오기
        original_channel_id = (
            body["view"]["private_metadata"]
            if body["view"].get("private_metadata")
            else body["user"]["id"]
        )

        # TODO: Supabase 연동 구현 필요
        await ack()

        # 원래의 채널에 회고 내용 게시
        await client.chat_postMessage(
            channel=original_channel_id,
            blocks=blocks,
            text="*<@{user_id}>님이 회고를 공유했어요! 🤗*",
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
