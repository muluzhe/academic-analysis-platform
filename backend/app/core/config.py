from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "学术内容智能分析平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list = ["*"]
    
    # AI API Configuration
    AI_API_KEY: str = ""
    AI_API_BASE: str = "https://api.deepseek.com/v1"
    AI_MODEL: str = "deepseek-chat"
    AI_MAX_TOKENS: int = 4096
    AI_TEMPERATURE: float = 0.7
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # Database
    DATABASE_URL: str = "sqlite:///./academic_analysis.db"
    
    # External APIs
    SEMANTIC_SCHOLAR_API: str = "https://api.semanticscholar.org/graph/v1"
    ARXIV_API: str = "http://export.arxiv.org/api/query"
    GITHUB_API: str = "https://api.github.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
