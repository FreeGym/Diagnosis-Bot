import os
from dotenv import load_dotenv, find_dotenv
import chromadb.utils.embedding_functions as embedding_functions
_ = load_dotenv(find_dotenv())

config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "max_tokens": 1000,
        "temperature": 0.6
    }
]

llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": config_list,
    "max_retries": 10
}

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
