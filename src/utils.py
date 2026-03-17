"""
Utility Functions
Helper functions for logging, configuration, and data processing
"""

import os
import logging
from dotenv import load_dotenv


def setup_logging(level=logging.INFO) -> None:
    """Setup logging configuration"""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def load_environment() -> dict:
    """Load environment variables from .env file"""
    load_dotenv()

    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4"),
        "temperature": float(os.getenv("TEMPERATURE", 0.7)),
        "max_tokens": int(os.getenv("MAX_TOKENS", 1000)),
        "chunk_size": int(os.getenv("CHUNK_SIZE", 500)),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", 100)),
        "max_results": int(os.getenv("MAX_RETRIEVAL_RESULTS", 3)),
        "data_folder": os.getenv("DATA_FOLDER", "data"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
    }

    return config


def ensure_directories() -> None:
    """Ensure required directories exist"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("embeddings", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


def format_response(response: str, sources: list) -> str:
    """Format response with source citations"""
    formatted = response

    if sources:
        formatted += "\n\n📚 **Sources:**\n"
        for source in set(sources):
            source_name = os.path.basename(source)
            formatted += f"- {source_name}\n"

    return formatted


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    return api_key.startswith("sk-") and len(api_key) > 20


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    text = " ".join(text.split())
    return text.strip()