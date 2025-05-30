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

## 서버 디버깅 가이드

### 서버 접속
```bash
ssh root@[서버IP] -p 22
```

### 도커 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 목록 확인
docker-compose -f docker-compose.prod.yaml ps

# 현재 활성화된 서버(blue/green) 확인
cat nginx/conf.d/default.conf
```

### 로그 확인
1. 애플리케이션 로그
```bash
# blue 서버 로그 (실시간)
docker-compose -f docker-compose.prod.yaml logs -f blue

# green 서버 로그 (실시간)
docker-compose -f docker-compose.prod.yaml logs -f green

# 마지막 100줄만 확인
docker-compose -f docker-compose.prod.yaml logs --tail=100 [blue|green]
```

2. nginx 로그
```bash
docker-compose -f docker-compose.prod.yaml logs -f nginx
```

### 컨테이너 내부 접속
```bash
# blue 서버 접속
docker-compose -f docker-compose.prod.yaml exec blue sh

# green 서버 접속
docker-compose -f docker-compose.prod.yaml exec green sh

# nginx 접속
docker-compose -f docker-compose.prod.yaml exec nginx sh
```

### 문제 해결
```bash
# 환경 변수 확인
docker-compose -f docker-compose.prod.yaml exec [blue|green] env

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yaml restart [blue|green]

# 서비스 재빌드
docker-compose -f docker-compose.prod.yaml up -d --build [blue|green]

# 전체 시스템 상태 확인
docker stats
```

### 컨테이너 종료

1. 컨테이너를 종료하고 리소스(네트워크, 볼륨 등)는 유지하는 경우:
```bash
docker-compose -f docker-compose.prod.yaml down
```

2. 컨테이너를 종료하고 모든 리소스(볼륨 포함)를 함께 삭제하는 경우:
```bash
docker-compose -f docker-compose.prod.yaml down -v
```

3. 실행 중인 컨테이너만 중지하고 싶은 경우:
```bash
docker-compose -f docker-compose.prod.yaml stop
```

4. 특정 서비스만 중지하고 싶은 경우:
```bash
docker-compose -f docker-compose.prod.yaml stop [blue|green]
```

### 유용한 팁
- 실시간 로그 확인 시 `-f` 옵션 사용
- 특정 서비스에 문제가 있을 경우 해당 서비스만 재시작
- 환경 변수 문제가 의심될 경우 컨테이너 내부에서 `env` 명령어로 확인
- nginx 설정 변경 후에는 nginx 컨테이너 재시작 필요

TODO:
- 에러 핸들링 ✅
- 에러 로그 관리자 채널에 알림 ✅
- supabase 테이블 컬럼 추가 ✅
  - 회차정보 ✅
  - 슬랙 채널 ✅
  - 슬랙 메시지 ts ✅
- crud 동작 확인 ✅
- 관리자 메뉴 추가 ✅
  - 관리자 아이디 추가 ✅
  - supabase 회고 데이터 및 슬랙 메시지 삭제 기능 ✅
  - supabase 회고 데이터 및 슬랙 메시지 업데이트 기능 ✅
- 문의 사항 남길 시 관리자 채널에 알림 ✅
- 자기 회고 내역 보기 ✅
- 뽀모도로 기능 추가 ✅
- 월요일 21시 리마인드 기능 (미제출자에 한함) 추후 참여자 명단과 채널이 나오면 진행
- 서버 띄우기 ✅