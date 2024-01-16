import os
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from .utils import to_snake_case, save_json
from .config_ import config_list, llm_config, openai_ef
from .dataloader import load_json
from typing import Annotated, Dict



class MedicalAgents:

    def __init__(self):
        self.agents = {}
        self.agents["compounderProxy"] = RetrieveUserProxyAgent(
            name="CompounderProxy",
            retrieve_config={
                "task": "qa",
                "docs_path": "data/docs/2_Questioning_Framework_Level_1.md",
                "model": config_list[0]["model"],
                "chunk_token_size": 2000,
                "embedding_model": "text-embedding-ada-002",
                "embedding_function": openai_ef,
                "get_or_create": True,
            },
            human_input_mode="TERMINATE",
            code_execution_config=True
        )

        self.agents["compounder"]= RetrieveAssistantAgent(
            name = "Compounder",
            description = "compounder: interviews patients about their health using a specified framework",
            system_message = """You are a compounder agent. \
                                Your job is to use a reference framework given in the context to ask patient questions pertaining to their health.\
                                DONOT forget to ask basic patient information such as NAME, AGE, GENDER
                                Remember to only ask ONE QUESTION AT A TIME.\
                                Once done , your job is to write the summary of the patient and the issues they are facing into a json file, \
                                using the _save_json function.\
                                You may `TERMINATE` the conversation post this.
                                If the context is irrelevant to the patient's query reply `I DON'T KNOW`
                                """,
            human_input_mode = "TERMINATE",
            llm_config = llm_config  
        )
        self.medical_professionals  = load_json()

        for medical_professional in self.medical_professionals.keys():
            for specialist in self.medical_professionals[medical_professional]:
                self.agents[to_snake_case(specialist["name"])] = RetrieveAssistantAgent(
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
            
    def _reset_agents(self):
        for agent in self.agents.keys():
            self.agents[agent].reset()
    
    def prelimnary_symptom_analysis(self,problem : str):
        
        @self.agents["compounderProxy"].register_for_execution()
        @self.agents["compounder"].register_for_llm(name="save_json", description="save a raw json string into a json file")
        def _save_json(raw_json_string : Annotated[str, "The raw JSON string to be saved"]) -> str:
            file_path = "data/user_symptoms.json"
            return save_json(raw_json_string,file_path)
            
        
        self._reset_agents()
        self.agents["compounderProxy"].initiate_chat(self.agents["compounder"],problem=problem)

    def select_agents(self,file_path="data/user_symptoms.json"):
        json_format = """{
                        "medical_professionals":[
                            "agent_1",
                            "agent_2",
                            "agent_n"
                        ]
                    }"""
        llm_agent = RetrieveAssistantAgent(
            name="assistant",
            system_message=f"""Your job is to assign skilled medical professionals to a patient basis their symptoms.
                             Given below are the names of the available medical professionals delimited by double backticks\
                    ``{list(self.agents.keys())}.
                    Write the raw JSON string of medical professionals from the available list who can treat the patient\
                    into a json file using the _save_json function.
                    STRICTLY ABIDE BY THE NAMING CONVENTION GIVEN IN THE LIST. DONOT CHANGE THE CASE OR NAMES
                    The JSON String should be of the following format 
                    `{json_format} `""",
            human_input_mode="NEVER",
            llm_config=llm_config
        )
        
        llm_proxy = RetrieveUserProxyAgent(
            name="UserProxy",
            retrieve_config={
                "task": "qa",
                "docs_path": "data/user_symptoms.json",
                "model": config_list[0]["model"],
                "chunk_token_size": 2000,
                "embedding_model": "text-embedding-ada-002",
                "embedding_function": openai_ef,
                "get_or_create": True,
            },
            human_input_mode="NEVER",
            code_execution_config=True,
            max_consecutive_auto_reply = 1
        )
        
        @llm_proxy.register_for_execution()
        @llm_agent.register_for_llm(name="save_json",description="save a raw json string into a json file")
        def _save_json(raw_json_string : Annotated[str, "The raw JSON string to be saved"]) -> str:
            file_path = "data/selected_agents.json"
            return save_json(raw_json_string,file_path)
        
        problem = f"""You are given below a patient's symptom details.Suggest the medical professionals they must visit"""
        llm_agent.reset()
        llm_proxy.reset()
        llm_proxy.initiate_chat(llm_agent,problem=problem,n_results=1)
