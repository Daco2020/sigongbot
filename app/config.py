from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = Field(default="dev")

    # Slack Environment
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str

    # Channel IDs
    ADMIN_CHANNEL: str = Field(default="C08QJQAPV54")
    SUPPORT_CHANNEL: str = Field(default="C08QM0S60LW")
    POMODORO_CHANNEL_ID: str = Field(default="C08QJQAPV54")  # TODO: 채널 변경하기

    # Admin IDs
    ADMIN_IDS: list[str]

    # Supabase Environment
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
