from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = Field(default="dev")

    # Slack Environment
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str

    # Channel IDs
    ADMIN_CHANNEL: str = Field(default="C08QJQAPV54")
    SUPPORT_CHANNEL: str = Field(default="C08QJQAPV54")

    # Supabase Environment
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
