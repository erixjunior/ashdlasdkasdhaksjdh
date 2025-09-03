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

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG").upper()
