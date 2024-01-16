import os
import json
from diagnosis_bot.medical_agents import MedicalAgents
import autogen
#TODO : Implement Stage-2 (function for choosing agents) 

def main():

    agents = MedicalAgents()
    problem = input("Hey there, welcome to the diagnosis bot. May I know your good name and the kind of health issues are you facing?\n" + "-" * 100 + "\n")
    prompt = f"""Please help with the diagnosis of the issues delimited by triple backticks 
                 ```{problem}```Do not show appreciation in your responses. If "Thank you" or "You're welcome" is said, 
                 then say TERMINATE to indicate the conversation is finished, and this is your last message."""
    
    agents.prelimnary_symptom_analysis(prompt)
    agents.select_agents()

if __name__ == "__main__":
    main()
