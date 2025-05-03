from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient


async def handle_command_retrospective(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """회고 제출 명령어 처리"""
    await ack()

    await client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "retrospective_submit",
            "title": {"type": "plain_text", "text": "회고 제출"},
            "submit": {"type": "plain_text", "text": "제출"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "good_points",
                    "label": {"type": "plain_text", "text": "잘했고 좋았던 것"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "good_points_input",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "improvements",
                    "label": {"type": "plain_text", "text": "개선점, 아쉬웠던 점"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "improvements_input",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "learnings",
                    "label": {"type": "plain_text", "text": "배운점"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "learnings_input",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "action_item",
                    "label": {"type": "plain_text", "text": "액션 아이템"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "action_item_input",
                        "multiline": True,
                    },
                },
                {
                    "type": "input",
                    "block_id": "emotion_score",
                    "label": {"type": "plain_text", "text": "오늘의 감정점수 (1-10)"},
                    "element": {
                        "type": "number_input",
                        "action_id": "emotion_score_input",
                        "is_decimal_allowed": False,
                        "min_value": "1",
                        "max_value": "10",
                    },
                },
                {
                    "type": "input",
                    "block_id": "emotion_reason",
                    "label": {"type": "plain_text", "text": "감정점수 이유"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "emotion_reason_input",
                        "multiline": True,
                    },
                },
            ],
        },
    )
