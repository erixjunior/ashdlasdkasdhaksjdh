import os
from dotenv import load_dotenv  # type: ignore

load_dotenv()


class Env:

    # Static variables for .env keys
    FACEBOOK_EMAIL: str = os.getenv("FACEBOOK_EMAIL")
    FACEBOOK_PASSWORD: str = os.getenv("FACEBOOK_PASSWORD")
    HEADLESS: bool = str(os.getenv("HEADLESS", "false")).lower() == "true"
    SLOW_MO_MS: int = int(os.getenv("SLOW_MO_MS", "1000"))
    MAX_POSTS_TO_SCRAPE: int = int(os.getenv("MAX_POSTS_TO_SCRAPE", "50"))
    SCRAPE_DELAY_MS: int = int(os.getenv("SCRAPE_DELAY_MS", "2000"))
    LOOP_INTERVAL: int = int(os.getenv("LOOP_INTERVAL", "30"))
    LOOP_TYPE: str = os.getenv("LOOP_TYPE", "continuous")

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG").upper()

    # AI configuration
    AI_API_KEY: str = os.getenv("AI_API_KEY")
    AI_ENDPOINT: str = os.getenv("AI_ENDPOINT")
    AI_MODEL: str = os.getenv("AI_MODEL")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.6"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "1024"))
