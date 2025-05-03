from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.logging import logger
from app.config import settings
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from app.slack.event_handler import app as slack_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작할 때 실행되는 코드
    logger.info("애플리케이션 시작")

    slack_handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=settings.SLACK_APP_TOKEN,
    )
    await slack_handler.connect_async()

    if settings.ENV == "prod":
        logger.info("프로덕션 환경에서 시작합니다")
        # 프로덕션 환경에서만 실행할 코드
    else:
        logger.info("개발 환경에서 시작합니다")
        # 개발 환경에서만 실행할 코드

    yield

    await slack_handler.close_async()

    logger.info("애플리케이션 종료")


app = FastAPI(lifespan=lifespan)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health(request: Request) -> dict:
    return {"message": "시공의 폭풍 속으로 ⛈️"}
