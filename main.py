import os
from dotenv import load_dotenv, find_dotenv
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb.utils.embedding_functions as embedding_functions
import autogen
import json
from utils import to_snake_case

_ = load_dotenv(find_dotenv()) 

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="text-embedding-ada-002"
            )

config_list = [
    {
          "model" : "gpt-3.5-turbo",
          "api_key" : os.getenv("OPENAI_API_KEY"),
          "max_tokens" : 1000,
          "temperature" : 0.3
    }  
]

agents = {}
agents["compounderProxy"] = RetrieveUserProxyAgent(
    name = "CompounderProxy",
    retrieve_config={
        "task" : "qa",
        "docs_path": "docs/",
        "model" : config_list[0]["model"],
        "chunk_token_size" : 2000,
        "embedding_model" : "text-embedding-ada-002",
        "embedding_function" : openai_ef,
        "get_or_create" : True,
    },
    human_input_mode="TERMINATE",
    code_execution_config = False
)


with open('medical_professionals.json', 'r') as file:
    data = json.load(file)
sports_medicine_specialists = data['sports_medicine_specialists']



agents["compounder"]= RetrieveAssistantAgent(
    name = "Compounder",
    description = "compounder: interviews patients about their health using a specified framework",
    system_message = """You are a compounder agent. \
                        Your job is to use a framework given in the context to ask patient questions pertaining to their health.\
                        Remember to only ask ONE QUESTION AT A TIME.\
                        Once you obtain primary symptom information from the patient, you present the case to Specialist Medical Agents in the group chat.\
                        At the end your job is to obtain the final diagnosis and convey the same to the patient.
                        If the context is irrelevant to the patient's query reply `I DON'T KNOW`
                        """,
    human_input_mode = "ALWAYS",
    llm_config = {
        "timeout": 600,
        "cache_seed": 42,
        "config_list": config_list,
        "max_retries" : 10
    }   
)

for sports_medicine_specialist in sports_medicine_specialists:
    agents[sports_medicine_specialist["name"]] = RetrieveAssistantAgent(
        name = to_snake_case(sports_medicine_specialist["name"]),
        description = sports_medicine_specialist["name"] + " : " + sports_medicine_specialist["description"],
        system_message = f"""
                        You are a {sports_medicine_specialist["name"]} and you specialise in {sports_medicine_specialist["description"]}.\
                        Your job is to convey the final diagnosis to the COMPOUNDER.
                        You may ask the patient clarifying questions regarding their symptoms. ASK ONE QUESTION AT A TIME. 
                        You may also converse with other medical experts in the group chat before arriving at the final diagnosis""",
        human_input_mode = "ALWAYS",
        llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
            "max_retries" : 10
        }   
    )

def _reset_agents():
    for agent in agents.keys():
        agents[agent].reset()

problem = input("Hey there , welcome to diagnosis bot? What kind of health issues are you facing ?\n" + "-"*100 +"\n")
# prompt = "I have knee pain"
# prompt = "What colour is the sky?" # Test prompt for checking hallucinations
prompt=f"""Please help with the diagnosis of the issues delimited by triple backticks 
        ```{problem}```"""
termination_notice = (
    '\n\nDo not show appreciation in your responses, say only what is necessary. '
    'if "Thank you" or "You\'re welcome" are said in the conversation, then say TERMINATE '
    'to indicate the conversation is finished and this is your last message.'
)
prompt += termination_notice

def _reset_agents() :
    for agent in agents.keys():
        agents[agent].reset()

llm_config = {
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
            "max_retries" : 10
        } 
  
def rag_chat():
    _reset_agents()
    groupchat = autogen.GroupChat(
        agents=list(agents.values()), messages=[], max_round=12
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss_aid as this is the user proxy agent.
    agents["compounderProxy"].initiate_chat(
        manager,
        problem=prompt,
        n_results=3,
    )

rag_chat()