import os
from dotenv import load_dotenv, find_dotenv
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# import chromadb
import chromadb.utils.embedding_functions as embedding_functions
# import openai

_ = load_dotenv(find_dotenv()) 

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )


config_list = [
    {
          "model" : "gpt-3.5-turbo",
          "api_key" : os.getenv('OPENAI_API_KEY'),
          "max_tokens" : 1000
    }
  
]


compounderProxy = RetrieveUserProxyAgent(
    name = "Compounder Proxy",
    retrieve_config={
        "task" : "qa",
        "docs_path": "docs/",
        "model" : config_list[0]["model"],
        "chunk_token_size" : 2000,
        "embedding_model" : "text-embedding-ada-002",
        "embedding_function" : openai_ef,
        "get_or_create" : True,
    },
    code_execution_config = False
)

compounderAgent = RetrieveAssistantAgent(
    name = "Compounder Agent",
    description = "compounder: interviews patients about their health using a specified framework",
    system_message = """You are a compounder agent. \
                        Your job is to use a framework given in the context to ask patient questions pertaining to their health.\
                        In case the patient doesn't ask anything related to sickness reply `YOU ARE HEALTHY , HAVE FUN`
                        If the context is irrelevant to the patient's query reply `I DON'T KNOW`
                        """,
    human_input_mode = "TERMINATE",
    llm_config = {
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
    }
    
)

prompt = "I am not feeling well for the past 2 days. Can you please help me ?"
termination_notice = (
    '\n\nDo not show appreciation in your responses, say only what is necessary. '
    'if "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
    'to indicate the conversation is finished and this is your last message.'
)
prompt += termination_notice

compounderProxy.initiate_chat(compounderAgent,problem=prompt,search_string="symptoms")