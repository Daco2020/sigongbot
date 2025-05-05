# 시공봇

## 슬랙 이벤트 핸들러 네이밍 컨벤션

### 기본 구조
`{action}_{event-type}_{feature-name}`

### 이벤트 타입별 접두사
- 슬래시 커맨드: `handle_command_*`
- 뷰/모달: `handle_view_*`
- 메시지 이벤트: `handle_message_*`
- 액션(버튼, 선택메뉴 등): `handle_action_*`
- 숏컷: `handle_shortcut_*`

### 예시
```python
# 슬래시 커맨드
@app.command("/공유")
async def handle_command_retrospective(...)

# 모달 뷰 제출
@app.view("retrospective_submit")
async def handle_view_retrospective_submit(...)

# 버튼 액션
@app.action("approve_button")
async def handle_action_retrospective_approve(...)

# 메시지 이벤트
@app.event("message")
async def handle_message_mention(...)

# 숏컷
@app.shortcut("quick_retro")
async def handle_shortcut_quick_retrospective(...)
```

### 규칙
1. 모든 핸들러 함수는 `handle_` 접두사로 시작
2. 두 번째 부분은 이벤트 타입 지정 (command, view, action, message, shortcut)
3. 마지막 부분은 해당 기능의 구체적인 이름
4. 모든 단어는 스네이크 케이스(_) 사용
5. 기능명은 명확하고 구체적으로 작성

### 장점
- 일관된 네이밍으로 코드 가독성 향상
- 이벤트 타입을 즉시 파악 가능
- 기능별 구분이 명확
- 향후 확장성을 고려한 구조
```

TODO:
- 에러 핸들링 v
- 에러 로그 관리자 채널에 알림 v 
- supabase 테이블 컬럼 추가
  - 회차정보
  - 채널
  - 메시지 아이디(ts)
- 서버 띄우기
- db di 리팩터링
- crud 동작 확인
- 관리자 메뉴 추가
  - 관리자 아이디 추가 v
  - 회고 데이터 및 메시지 삭제 기능
  - 회고 데이터 및 메시지 업데이트 기능 (안쓰는게 좋을 듯)
- 문의 사항 남길 시 관리자 채널에 알림
- 월요일 21시 리마인드 기능 (미제출자에 한함)
- 자기 회고 내역 보기 및 csv 파일 다운로드 기능