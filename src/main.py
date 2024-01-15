import os
import json
from diagnosis_bot.medical_agents import initialize_agents, _reset_agents
from diagnosis_bot.config_ import llm_config
import autogen


#TODO : Implement Stage-1 (chat between compounder agent and Userproxy)
#TODO : Implement Stage-2 (function for choosing agents) 



def main():
#     _ = load_dotenv(find_dotenv())

    agents = initialize_agents()

    problem = input("Hey there, welcome to the diagnosis bot. What kind of health issues are you facing?\n" + "-" * 100 + "\n")

    prompt = f"""Please help with the diagnosis of the issues delimited by triple backticks 
                 ```{problem}```Do not show appreciation in your responses. If "Thank you" or "You're welcome" is said, 
                 then say TERMINATE to indicate the conversation is finished, and this is your last message."""

    _reset_agents(agents)

    groupchat = autogen.GroupChat(
        agents=list(agents.values()), messages=[], max_round=12
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    agents["compounderProxy"].initiate_chat(
        manager,
        problem=prompt,
        n_results=3,
    )

if __name__ == "__main__":
    main()
