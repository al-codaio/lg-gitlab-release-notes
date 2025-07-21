from pydantic import BaseSettings

class Settings(BaseSettings):
    gitlab_url: str = "https://gitlab.com"
    gitlab_private_token: str
    openai_api_key: str
    project_id: str
    
    # Optional settings
    max_retries: int = 3
    timeout: int = 30
    default_lookback_days: int = 30
    
    class Config:
        env_file = ".env"