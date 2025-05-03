# 베이스 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /workspace

# 필요한 패키지 설치 및 Poetry 설치
RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetry를 PATH에 추가
ENV PATH="/root/.local/bin:$PATH"

# Poetry 설정: 가상환경을 프로젝트 외부에 생성하도록 설정
RUN poetry config virtualenvs.create false

# 프로젝트의 Poetry 설정 파일 복사 및 종속성 설치
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root

# 애플리케이션 코드 복사
COPY ./app ./app
COPY ./scripts ./scripts

# 스크립트 실행 권한 설정
RUN chmod +x scripts/*.sh

# 환경 변수는 docker-compose에서 관리
CMD ["scripts/prod.sh"]
