import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# from supabase import create_client, Client

# 환경 변수 로드
load_dotenv()

# Slack 앱 초기화
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# # Supabase 클라이언트 초기화
# supabase: Client = create_client(
#     os.environ.get("SUPABASE_URL", ""),
#     os.environ.get("SUPABASE_KEY", "")
# )


@app.command("/공유")
def handle_submit_command(ack, body, client):
    """회고 제출 명령어 처리"""
    ack()

    # 모달 열기
    client.views_open(
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


@app.view("retrospective_submit")
def handle_submission(ack, body, client, view):
    """모달 제출 처리"""
    # 사용자 입력 데이터 추출
    user_id = body["user"]["id"]
    # values = view["state"]["values"]

    # submission_data = {
    #     "user_id": user_id,
    #     "good_points": values["good_points"]["good_points_input"]["value"],
    #     "improvements": values["improvements"]["improvements_input"]["value"],
    #     "learnings": values["learnings"]["learnings_input"]["value"],
    #     "action_item": values["action_item"]["action_item_input"]["value"],
    #     "emotion_score": int(values["emotion_score"]["emotion_score_input"]["value"]),
    #     "emotion_reason": values["emotion_reason"]["emotion_reason_input"]["value"],
    #     "submitted_at": "now()",
    # }

    try:
        # Supabase에 데이터 저장
        # supabase.table("retrospectives").insert(submission_data).execute()

        # 성공 메시지 전송
        ack()
        client.chat_postEphemeral(
            channel=body["user"]["id"],
            user=user_id,
            text="회고가 성공적으로 제출되었습니다! 🎉",
        )
    except Exception:
        # 에러 처리
        ack(
            response_action="errors",
            errors={
                "good_points": "데이터 저장 중 오류가 발생했습니다. 다시 시도해주세요."
            },
        )


if __name__ == "__main__":
    # 소켓 모드로 앱 실행
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
