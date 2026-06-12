from pydantic_settings import BaseSettings
from pydantic import Field



class Settings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY: str = Field(..., env="AZURE_OPENAI_KEY")
    AZURE_DEPLOYMENT_NAME: str = Field(..., env="AZURE_DEPLOYMENT_NAME")

    # NEO4J Settings
    NEO4J_URI: str = Field("bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USERNAME: str = Field("neo4j", env="NEO4J_USERNAME")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")
    NEO4J_DATABASE: str = Field("neo4j", env="NEO4J_DATABASE")

    # Database Settings
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./medical_rag.db", env="DATABASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()