
import json
from typing import Annotated
from flask import jsonify
import autogen
from autogen import UserProxyAgent
from autogen import AssistantAgent
import os
from dotenv import load_dotenv, find_dotenv
import tempfile

from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor

_ = load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
GROQ_API_KEY = os.environ['GROQ_API_KEY']

toxicity_prompt = '''
**Role**: You are a toxicity check expert. Analyze the following text for potential toxic words.Consider only text after "Message : " from input message to process.
Ignore any other details which are not offensive or foul language.

If there is no toxic content,
    Return original text with "NOT DETECTED" at the start of message

Else return reponse as key value pair with keys as Content, Toxicity Score, Toxicity Category represented in bold.
    Content : Which part of input message is identified toxic
    Toxicity Level : select one of values High,Medium, Low
    Toxicity Category : category as mentioned above
    Please mention "DETECTED" at the start of the message
    Please add "Message : " and original input message at the end

'''


sensitivity_prompt = '''
**Role**: You are a sensitive data check expert. Analyze the input message for sensitive financial data only. Dont assume anything and make sure if direct financial information is present or requested.
Ignore any other sensitive data.

If there is no sensitive financial data found,
    Return original text with "NOT DETECTED" at the start of message

Else return reponse as key value pair with keys as Content, Sensitivity Category represented in bold at the end.
    Content : Which part of input message is identified toxic
    Sensitivity Category : category as mentioned above
    Please mention "DETECTED" at the start of the message
    Please add "Message : " and original input message at the end
'''

pii_prompt = '''
**Role**: You are a PII data check expert. You need to detect any PII information in the given input message.Consider only text after "Message : " from input message to process.

If there is no any PII information,
    Return original text with "NOT DETECTED" at the start of message

Else mask any type of PII data identified in the input message with letter XXXXXXXX.
    Return the masked message as response without any alteration.Mask any PII information identified.Ignore names of person.
    Please mention "DETECTED" at the start of the message
'''

config_list = [{'model': 'gemini-1.5-flash', 'api_key': GOOGLE_API_KEY,"api_type": "google"}]

llm_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

groq_config_list = [
    {
        "api_type": "groq",
        "model":"llama3-8b-8192",
        "api_key": GROQ_API_KEY
    }
]


user_proxy = autogen.UserProxyAgent(
    name="Initial User",
    system_message = "A user starting the conversation",
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },  
    human_input_mode="NEVER",
)

human_proxy = autogen.ConversableAgent(
    "human_proxy",
    llm_config=False,  # no LLM used for human proxy
    human_input_mode="ALWAYS",  # always ask for human input
)

# class Toxicity_Check_Agent(AssistantAgent):
#     """
#     An assistant agent focused on identifying toxic content within messages using a provided toxicity prompt.
#     It leverages code execution capabilities for analysis and operates within a specified work directory.
#
#     Args:
#         name (str): The name of the agent, defaults to "Toxicity Check Agent".
#         system_message (str): The prompt containing instructions for toxicity detection.
#         llm_config (dict): Language model configuration settings.
#         code_execution_config (dict): Configuration for code execution, including work directory and Docker usage.
#
#     @version 1.0.2
#     @author Ajay
#     """
toxicity_check_agent = AssistantAgent(
    name = "Toxicity Check Agent",
    system_message = toxicity_prompt,
    llm_config={"config_list": config_list},
    code_execution_config={
        # "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    # is_termination_msg=lambda msg: "is blocked" in msg["content"].lower(),
)

# class Sensitivity_Check_Agent(AssistantAgent):
#     """
#     An assistant agent designed to identify sensitive content within messages based on a provided sensitivity prompt.
#     It utilizes code execution and operates within a defined work directory for content analysis.
#
#     Args:
#         name (str): The name of the agent, defaults to "Sensitivity Check Agent".
#         system_message (str): The prompt containing instructions for sensitivity detection.
#         llm_config (dict): Language model configuration settings.
#         code_execution_config (dict): Configuration for code execution, including work directory and Docker usage.
#
#     @version 1.0.2
#     @author Ajay
#     """
sensitivity_check_agent = AssistantAgent(
    name = "Sensitivity Check Agent",
    system_message = sensitivity_prompt,
    llm_config={"config_list": config_list},
    code_execution_config={
        # "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    # is_termination_msg=lambda msg: "is blocked" in msg["content"].lower(),
)

# class PII_Check_Agent(AssistantAgent):
#     """
#     An assistant agent focused on identifying Personally Identifiable Information (PII) within messages using a PII prompt.
#     It leverages code execution capabilities and operates within a specified work directory for PII detection.
#
#     Args:
#         name (str): The name of the agent, defaults to "PII Check Agent".
#         system_message (str): The prompt containing instructions for PII detection.
#         code_execution_config (dict): Configuration for code execution, including work directory and Docker usage.
#         llm_config (dict): Language model configuration settings.
#
#     @version 1.0.2
#     @author Ajay
#     """
pii_check_agent = AssistantAgent(
    name = "PII Check Agent",
    system_message = pii_prompt,
    code_execution_config={
        # "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    llm_config={"config_list": config_list}
)


# class Keyword_Check_Agent(AssistantAgent):
#     """
#     An assistant agent designed to detect keywords within input messages by executing the 'detect_keywords' function.
#     It is configured for code execution and utilizes a specific Groq language model configuration.
#
#     Args:
#         name (str): The name of the agent, defaults to "Keyword Check Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'detect_keywords'.
#         code_execution_config (dict): Configuration for code execution, including work directory and Docker usage.
#         llm_config (dict): Language model configuration settings for Groq.
#
#     @version 1.0.2
#     @author Ajay
#     """
keyword_check_agent = AssistantAgent(
    name = "Keyword Check Agent",
    system_message ="You should execute function detect_keywords by passing complete input message as argument.",
    code_execution_config={
        # "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    llm_config={"config_list": groq_config_list}
)

# class Keyword_Identifier(autogen.UserProxyAgent):
#     """
#     A user proxy agent responsible for executing functions, specifically for keyword identification tasks.
#     It is configured for code execution and operates in a 'NEVER' human input mode.
#
#     Args:
#         name (str): The name of the agent, defaults to "Keyword Identifier".
#         system_message (str): Instructions for the agent, specifying function execution.
#         code_execution_config (dict): Configuration for code execution, including work directory and Docker usage.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
keyword_executor = autogen.UserProxyAgent(
    name="Keyword Identifier",
    system_message = "Execute function",
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    human_input_mode="NEVER",
)


@keyword_executor.register_for_execution()
@keyword_check_agent.register_for_llm(description="You should execute the function")
def detect_keywords(message:str) -> str:
    print("function calling", message)
    file_key = ""
    # if "PANACEA - " in message:
    #     file_key = "panaceakeywords"
    # elif "SENTINEL - " in message:
    #     file_key = "sentinelkeywords"
    keys = ["panaceakeywords","sentinelkeywords"]
    keywords = []
    i = 0
    with open("keywords.json", 'r') as file:
        data = file.read()
        keywords_json = json.loads(data)
        for key in keys:
            keywords.extend(keywords_json[key])
        for word in keywords:
            if word in message:
                i=i+1
                message = message.replace(word,"XXXXXXXXX")
        if i==0:
            message = "NOT DETECTED "+message
        else:
            message = "DETECTED "+message
    return message

def state_transition(last_speaker, groupchat):
    messages = groupchat.messages
   
    if last_speaker is user_proxy:
        return sensitivity_check_agent
    elif last_speaker is sensitivity_check_agent:
        return toxicity_check_agent
    elif last_speaker is toxicity_check_agent:
        return pii_check_agent
    elif last_speaker is pii_check_agent:
        return keyword_check_agent
    elif last_speaker is keyword_check_agent:
        # return human_proxy
        return keyword_executor
    elif last_speaker is keyword_executor:
        return None
  
   


groupchat = autogen.GroupChat(
    agents=[user_proxy, sensitivity_check_agent,toxicity_check_agent,pii_check_agent,keyword_check_agent,keyword_executor], 
    messages=[],
    speaker_selection_method=state_transition,
    # max_round=3
)

# groupchat = autogen.GroupChat(
#     agents=[user_proxy, sensitivity_check_agent,toxicity_check_agent,pii_check_agent,keyword_check_agent,keyword_executor,human_proxy], 
#     messages=[],
#     speaker_selection_method=state_transition,
#     # max_round=3
# )
groupchat_manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# user_proxy.initiate_chat(groupchat_manager, message="Panacea - Get details of AmyCripto who needs treatment of Xotoxin")
# messages = user_proxy.chat_messages[groupchat_manager]

  