import os
import json
import ast
import pandas as pd
import time
import autogen
from autogen import ConversableAgent
from LLMConfig import *
example={
  "title": "North America",
  "latitude": 39.563353,
  "longitude": -99.316406,
  "width": 30,
  "height": 30,
  "pieData": [{
    "category": "Compliance",
    "value": 0
  }, {
    "category": "Risk Assessment",
    "value": 0
  }, {
    "category": "PII Data",
    "value": 0
  }
  ]
}
folder_path="../static/MedicalCodes"
all_headers = []
file_count=0
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_count=file_count+1
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_csv(file_path)
            all_headers.extend(df.columns.tolist()) 
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

return_json=[]
id_list= ["US", "GB", "CN", "IN", "AU", "CA", "BR", "ZA"]
country_list= ["United States", "United Kingdom", "China", "India", "Australia", "Canada", "Brasil", "South Africa"]
country_list_new= ["United States", "United Kingdom"]
Compliance_Assessment_Agent_Prompt = "For the first call , pass the country name input message as it is and for the second call, give me the output in this format of list of jsons "+str(example)+" in the country giving approximate latitude and longitude values of central point. For Getting the actual value of PII Data, Risk Assessmeny And Compliance in json use output from the nested chat agents and take values which are non zero.  Response should be the a single list that will have all of column names having PII and Compliance issue and risk assessment count of columns in value field in the mentioned country without any extra text or strings or notes "
        
# Compliance_Assessment_Agent_Prompt = "Given list of column names  "


global_compliance_agent = autogen.AssistantAgent(
    name="Global_Compliance_Agent",
    llm_config={"config_list": config_list},
    system_message=Compliance_Assessment_Agent_Prompt,
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

agent_proxy = autogen.UserProxyAgent(
    name="Agent Proxy",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

# class Attribute_Compliance_Agent(autogen.AssistantAgent):
#     """
#     An assistant agent focused on checking attribute compliance.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Attribute_Compliance_Agent".
#         llm_config (dict): Configuration for the language model.
#         system_message (str): The system message defining the agent's role and instructions.
#
#     @version 1.0.2
#     @author Ajay
#     """

attribute_compliancecheck_agent = autogen.AssistantAgent(
    name="Attribute_Compliance_Agent",
    llm_config={"config_list": config_list},
    system_message="Given the list of columns names \n\n" + str(all_headers) + "\n\n in a database table, give me the count of columns tha will be giving Compliance issues. return response in the same format as input json after replacing Compliance category value with value as count of compliance issue columns identifed. Dont return any additional text or notes",
)

# class Dataleakage_Risk_Agent(autogen.AssistantAgent):
#     """
#     An assistant agent focused on identifying data leakage risks.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Dataleakage_Risk_Agent".
#         llm_config (dict): Configuration for the language model.
#         system_message (str): The system message defining the agent's role and instructions.
#
#     @version 1.0.2
#     @author Ajay
#     """

dataleakage_risk_agent = autogen.AssistantAgent(
    name="Dataleakage_Risk_Agent",
    llm_config={"config_list": config_list},
    system_message="Given the list of columns names \n\n" + str(all_headers) + \
            "\n\n in a database table, give me the count of columns tha will be giving Risk issue. return response in the same format as input json after replacing Risk Assessment category value with value as count of risk columns identifed.Dont return any additional text or notes",
)


# class Hipaa_Compliance_Agent(autogen.AssistantAgent):
#     """
#     An assistant agent focused on identifying HIPAA compliance issues (Hipaa Compliance).
#
#     Args:
#         name (str): The name of the agent. Defaults to "Hipaa_Compliance_Agent".
#         llm_config (dict): Configuration for the language model.
#         system_message (str): The system message defining the agent's role and instructions.
#
#     @version 1.0.2
#     @author Ajay
#     """

hipaa_compliance_agent = autogen.AssistantAgent(
    name="Hipaa_Compliance_Agent",
    llm_config={"config_list": config_list},
    system_message="Given the list of columns names \n\n" + str(all_headers) + \
            "\n\n in a database table, give me the count of columns tha will be giving PII Details.return response in the same format as input after replacing PII Data value with value as count of pii data columns identifed.Dont return any additional text or notes",
)



def reflection_message(recipient, messages, sender, config):
    print("Reflecting...", "")
    return f"Return expected response based on the below message. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


user_proxy.register_nested_chats(
    [
        {
            "sender":agent_proxy,
            "recipient": attribute_compliancecheck_agent,
            "max_turns": 1,
            "message": reflection_message,
        },
        {
            "sender":attribute_compliancecheck_agent,
            "recipient": dataleakage_risk_agent,
            "max_turns": 1,
            "message": reflection_message,
        },
        {
            "sender":dataleakage_risk_agent,
            "recipient": hipaa_compliance_agent,
            "max_turns": 1,
            "message": reflection_message,
        }
    ],
    trigger=global_compliance_agent,  # condition=my_condition,
)

# res = user_proxy.initiate_chats(recipient=global_compliance_agent, message="United States", max_turns=2, summary_method="last_msg")



json_list = []
for country in country_list_new:
    json_list.append({
        "recipient": global_compliance_agent,
        "message": country,
        "max_turns": 2,
        "summary_method": "last_msg",
    })



def ComplianceAssessment():
    chat_results = user_proxy.initiate_chats(json_list)

    summary = []
    for chat_result in chat_results:
        text = chat_result.summary.replace("```json","")
        text = text.replace("```","")
        val=ast.literal_eval(text)
        summary.append(val[0])
    return_dict={
        "file_count":file_count,
        "column_count":len(all_headers),
        "chart_data":summary
    }
    print("Final Output",return_dict)
    return return_dict

ComplianceAssessment()