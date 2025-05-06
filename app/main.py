from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.logging import logger
from app.config import settings
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from app.slack.event_handler import app as slack_app
from app.slack.pomodoro_scheduler import start_pomodoro_scheduler
import asyncio


# 전역 변수로 스케줄러 태스크 저장
pomodoro_scheduler_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작할 때 실행되는 코드
    logger.info("애플리케이션 시작")
    global pomodoro_scheduler_task

    slack_handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=settings.SLACK_APP_TOKEN,
    )
    await slack_handler.connect_async()

    # 뽀모도로 스케줄러를 백그라운드 태스크로 실행 (전역 변수에 저장)
    pomodoro_scheduler_task = asyncio.create_task(
        start_pomodoro_scheduler(slack_app.client)
    )
    logger.info("뽀모도로 스케줄러가 백그라운드에서 시작되었습니다")

    if settings.ENV == "prod":
        logger.info("프로덕션 환경에서 시작합니다")
        # 프로덕션 환경에서만 실행할 코드
    else:
        logger.info("개발 환경에서 시작합니다")
        # 개발 환경에서만 실행할 코드

    yield

    # 애플리케이션 종료 시 스케줄러 태스크 취소
    if pomodoro_scheduler_task and not pomodoro_scheduler_task.done():
        pomodoro_scheduler_task.cancel()
        try:
            await pomodoro_scheduler_task
        except asyncio.CancelledError:
            logger.info("뽀모도로 스케줄러가 정상적으로 종료되었습니다")

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
