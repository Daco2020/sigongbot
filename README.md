# 회고 수집 슬랙 봇

일일 회고를 수집하고 Supabase에 저장하는 Slack 봇입니다.

## 설정 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. `.env` 파일 생성 및 설정:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

3. Supabase에서 `app/database/schema.sql` 파일의 내용을 실행하여 테이블을 생성합니다.

4. 애플리케이션 실행:
```bash
python app/main.py
```

## Slack 앱 설정

1. [Slack API](https://api.slack.com/apps) 페이지에서 새 앱 생성
2. Socket Mode 활성화
3. 다음 Bot Token Scopes 추가:
   - `chat:write`
   - `commands`
   - `users:read`
4. 슬랙 워크스페이스에 앱 설치
5. `/제출` 슬래시 명령어 생성

## 사용 방법

1. 슬랙에서 `/제출` 명령어 입력
2. 모달 창에서 다음 항목 작성:
   - 잘했고 좋았던 것
   - 개선점, 아쉬웠던 점
   - 배운점
   - 액션 플랜
   - 오늘의 감정점수(1-10)와 이유
3. 제출 버튼 클릭 