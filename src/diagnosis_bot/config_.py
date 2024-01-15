import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "max_tokens": 1000,
        "temperature": 0.3
    }
]

llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": config_list,
    "max_retries": 10
}
