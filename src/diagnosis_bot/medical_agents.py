import os
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import autogen
from .utils import to_snake_case, save_json
from .config_ import config_list, llm_config, openai_ef
from .dataloader import load_json
from typing import Annotated



class MedicalAgents:

    def __init__(self):
        self.agents = {}
        self.agents["compounderProxy"] = RetrieveUserProxyAgent(
            name="CompounderProxy",
            retrieve_config={
                "task": "qa",
                "docs_path": "data/docs/",
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
                                Your job is to use a basic reference framework given in the context to ask patient questions pertaining to their health.\
                                DONOT forget to ask basic patient information such as NAME, AGE, GENDER
                                Remember to only ask ONE QUESTION AT A TIME. Validate the answer for each question.\
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
                        Your job is to convey the final diagnosis to the ChatManager Agent.
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
        self.agents["compounderProxy"].initiate_chat(self.agents["compounder"],problem=problem, search_string="basic framework")

    def select_agents(self,file_path="data/user_symptoms.json"):
        print("Hi dude , I was called")
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
                    into a json file using the _save_json function.DO NOT ASSUME ANY INFORMATION.\
                    STRICTLY ABIDE BY THE NAMING CONVENTION GIVEN IN THE LIST. DO NOT CHANGE THE CASE OR NAMES. \
                    CHOOSE ATLEAST 3 specialist agents
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
                "get_or_create": False,
                "collection_name" : "patient-docs"
            },

            human_input_mode="NEVER",
            code_execution_config=True,
            max_consecutive_auto_reply = 1
        )

        @llm_proxy.register_for_execution()
        @llm_agent.register_for_llm(name="save_json",description="save a raw json string into a json file")
        def _save_json(raw_json_string : Annotated[str, "The raw JSON string to be saved"]) -> str:
            os.system("touch data/selected_agents.json")
            file_path = "data/selected_agents.json"
            return save_json(raw_json_string,file_path)
        
        problem = f"""You are given below a patient's symptom details.Suggest the medical professionals they must visit"""
        llm_agent.reset()
        llm_proxy.reset()
        llm_proxy.initiate_chat(llm_agent,problem=problem,n_results=1)

    def perform_final_diagnosis(self):
        selected_agents = load_json("data/selected_agents.json")["medical_professionals"]
        user_symptoms = load_json("data/user_symptoms.json")
        # self.agents["compounderProxy"].retrieve_config.update()
        self._reset_agents()
        groupchat = autogen.GroupChat(
            agents=[self.agents[agent] for agent in selected_agents], messages=[], max_round=25)
        manager = autogen.GroupChatManager(
            groupchat=groupchat, 
            llm_config=llm_config,
            system_message="You are a chat manager. Your job is to facilitate the smooth discussion between the medical agents.\
                            At the end of the discussion, gather consensus from the experts in the groupchat and deliver the final \
                            patient diagnosis.Write the final diagnosis into a JSON file using the _save_json function",
            human_input_mode="ALWAYS"
        )

        PROBLEM = f"""Given below are my personal and basic symptoms details of in the JSON string delimited by triple backticks\
                {user_symptoms}. Provide a detailed diagnosis of what I could be suffering from. \
                You may ask me clarifying questions pertaining to my health if any.\
                Do not show appreciation in your responses. If "Thank you" or "You're welcome" is said, 
                then say TERMINATE to indicate the conversation is finished, and this is your last message."""
        @self.agents["compounderProxy"].register_for_execution()
        @manager.register_for_llm(name="save_json",description="save a raw json string into a json file")
        def _save_json(raw_json_string : Annotated[str, "The raw JSON string to be saved"]) -> str:
            file_path = "data/final_diagnosis.json"
            return save_json(raw_json_string,file_path)

        self._reset_agents()
        self.agents["compounderProxy"].initiate_chat(
            manager,
            problem=PROBLEM,
            n_results=3,
            search_string="detailed description"
        )
        
