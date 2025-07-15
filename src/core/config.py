"""
Core configuration module for Azure FastAPI application.
Following FHS architecture principles.
"""
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "Azure FastAPI Resume API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # Azure OpenAI settings
    openai_api_key: str = ""
    openai_api_base: str = "https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com"
    openai_api_version: str = "2023-05-15"
    openai_deployment_name: str = "gpt-4o-2"
    
    # LLM settings for keyword extraction
    llm_temperature: float = 0.0
    llm_max_tokens: int = 1000
    llm_seed_round1: int = 42
    llm_seed_round2: int = 43
    
    # Embedding settings (for general embeddings)
    embedding_endpoint: str = "https://wenha-m7qan2zj-swedencentral.cognitiveservices.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-3-large"
    
    # Course embedding settings (for course search)
    course_embedding_endpoint: str = "https://ai-azureai700705952086.cognitiveservices.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15"
    course_embedding_api_key: str = ""
    course_embedding_model: str = "text-embedding-3-small"
    
    # Similarity calculation settings
    sigmoid_x0: float = 0.373
    sigmoid_k: float = 15.0
    keyword_match_case_sensitive: bool = False
    enable_plural_matching: bool = True
    
    # Gap Analysis settings
    gap_analysis_temperature: float = 0.7
    gap_analysis_max_tokens: int = 2000
    
    # Security settings
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # CORS settings - secured for production
    cors_origins: str = "https://airesumeadvisor.com,https://airesumeadvisor.bubbleapps.io,http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "Content-Type,Authorization,X-Requested-With"
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore unknown environment variables
        
    @property
    def cors_origins_list(self):
        """Convert CORS origins string to list for FastAPI."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return ["*"]
    
    @property 
    def cors_allow_methods_list(self):
        """Convert CORS methods string to list for FastAPI."""
        if isinstance(self.cors_allow_methods, str):
            return [method.strip() for method in self.cors_allow_methods.split(",")]
        return ["*"]
        
    @property
    def cors_allow_headers_list(self):
        """Convert CORS headers string to list for FastAPI."""
        if isinstance(self.cors_allow_headers, str):
            return [header.strip() for header in self.cors_allow_headers.split(",")]
        return ["*"]
    
    def get_openai_config(self) -> dict[str, Any]:
        """Get OpenAI configuration dictionary."""
        return {
            "api_key": self.openai_api_key,
            "api_base": self.openai_api_base,
            "api_version": self.openai_api_version,
            "deployment": self.openai_deployment_name,
        }


# Create global settings instance
settings = Settings()


# Dependency injection functions
def get_settings() -> Settings:
    """
    Dependency injection for application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return settings
