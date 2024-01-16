# The Prompt Algorithm

## Draft 1

1. Ask the patient/user for the most basic description of their condition, as laypeople cannot express health issues in precise medical terms. Consider every piece of information step-by-step and verify before making any decisions.
2. Based on that description, make a judgment on what kind of medical professionals are best suited for diagnosing the condition by reviewing the document named `1_List_of_Medical_Professionals.pdf`. Consider every piece of information step-by-step and verify before making any decisions.
3. Ask the patient all the relevant questions based on the document `2_Questioning_Framework_Level_1.pdf`.
4. Based on the patient's initial description and all the answers to the questions crafted from the document `2_Questioning_Framework_Level_1.pdf`, create expert AI agents representing these medical professionals to hypothesize a preliminary diagnosis. They should be following Occam's razor principle. Consider every piece of information step-by-step and verify before making any decisions.
5. Consider every piece of information provided by the experts, process them thoroughly, and review the file named `3_Primary_Complaint_Symptom_Level_2.pdf` to craft questions that are the most relevant to the context so far. Consider every piece of information step-by-step and verify before making any decisions.
6. Again, consider every piece of information collected so far, process them thoroughly, and review the document named `4_Health_History_Level_2.pdf` to craft questions that are the most relevant to the context so far. Consider every piece of information step-by-step and verify before making any decisions.
7. One more time, consider every piece of information collected so far, process them thoroughly, and then review the document named `5_Lifestyle_Factors_Level_2.pdf` to craft questions that are the most relevant to the context so far. Consider every piece of information step-by-step and verify before making any decisions.
8. Repeat it again, consider every piece of information collected so far, process them thoroughly, and then review the document named `6_Environmental_Occupational_Factors_Level_2.pdf` to craft questions that are the most relevant to the context so far. Consider every piece of information step-by-step and verify before making any decisions.
9. Based on the entire processing, come up with the best diagnoses.
10. It’s important to follow this algorithm step-by-step and not mix it up.


## Draft 2 
Proposed workflow split into 3 stages : 

STAGE #1 : 
    - GOAL : Prelimnary diagnosis of patient. Compounder does primary symptoms assessment and then provides a summary of the same
    - Agents involved (UserProxyAgent, CompounderAgent)

STAGE #2 : 
    - GOAL : Takes the summary of patient's primary symptom and selects the list of medical agents to perform diagnosis
    - Agents involved (AssistantAgent)
    - INPUT : Summary + Python List of All Specialists 
    - OUTPUT : A python list of subset of specialists required for the issue

STAGE #3 : 
    - GOAL : To do the final groupchat and arrive at the final diagnosis
    - Agents involved (ChatManager, list of agents obtained from stage-2, UserProxy)