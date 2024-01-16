import os
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from .utils import to_snake_case, json_string_to_dict
from .config_ import config_list, llm_config, openai_ef
from .dataloader import load_medical_professionals
from typing import Annotated, Dict
import json


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
                                using the save_json function.\
                                You may `TERMINATE` the conversation post this.
                                If the context is irrelevant to the patient's query reply `I DON'T KNOW`
                                """,
            human_input_mode = "TERMINATE",
            llm_config = llm_config  
        )
        medical_professionals  = load_medical_professionals()

        for medical_professional in medical_professionals.keys():
            for specialist in medical_professionals[medical_professional]:
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
    
    def prelimnary_symptom_analysis(self,problem : str) -> str:
        
        @self.agents["compounderProxy"].register_for_execution()
        @self.agents["compounder"].register_for_llm(name="save_json", description="save a raw json string to python variable")
        def save_json(raw_json_string : Annotated[str, "The raw JSON string to be saved"]) -> str:
            file_path = "data/user_symptoms.json"
            try:
                data = json.loads(raw_json_string)
                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                print(f'JSON data has been written to {file_path}')
            except json.JSONDecodeError as e:
                print(f'Error decoding JSON: {e}')
            return ""
        
        self._reset_agents()
        self.agents["compounderProxy"].initiate_chat(self.agents["compounder"],problem=problem)

