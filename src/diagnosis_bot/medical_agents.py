import os
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb.utils.embedding_functions as embedding_functions
from .utils import to_snake_case
from .config_ import config_list, llm_config
from .dataloader import load_medical_professionals

def initialize_agents():
    agents = {}
    
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-ada-002"
    )

    agents["compounderProxy"] = RetrieveUserProxyAgent(
        name="CompounderProxy",
        retrieve_config={
            "task": "qa",
            "docs_path": "data/docs",
            "model": config_list[0]["model"],
            "chunk_token_size": 2000,
            "embedding_model": "text-embedding-ada-002",
            "embedding_function": openai_ef,
            "get_or_create": True,
        },
        human_input_mode="TERMINATE",
        code_execution_config=False
    )

    medical_professionals  = load_medical_professionals()

    for medical_professional in medical_professionals.keys():
        for specialist in medical_professionals[medical_professional]:
            agents[to_snake_case(specialist["name"])] = RetrieveAssistantAgent(
                name=to_snake_case(specialist["name"]),
                description=specialist["name"] + " : " + specialist["description"],
                system_message=f"""
                    You are a {specialist["name"]} and you specialize in {specialist["description"]}.\
                    Your job is to convey the final diagnosis to the COMPOUNDER.
                    You may ask the patient clarifying questions regarding their symptoms. ASK ONE QUESTION AT A TIME. 
                    You may also converse with other medical experts in the group chat before arriving at the final diagnosis""",
                human_input_mode="ALWAYS",
                llm_config=llm_config
            )
    return agents

def _reset_agents(agents):
    for agent in agents.keys():
        agents[agent].reset()
