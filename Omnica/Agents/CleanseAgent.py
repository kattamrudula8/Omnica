import os
import time
import autogen
from autogen import ConversableAgent
from Agents.DataNormalizationAgent import data_normalization_agent
from Agents.LLMConfig import *
from socket_io_setup import socketio

Role = """
    **Role** :  You are a data analyst expert in interpreting list of data and identifies abnormalities to provide accurate diagnoses..
                Input values are of first 100 data of a column of csv will be provided to you, there might be mixed up data like 
                INTEGER, Float, VARCHAR and your task is to update list with uniform respective values matching the data
                type to the maximum occupied values in list
                """

Multi_Language_Cleansing_Prompt = """
    **Task** :  if the list values are in different languages change values all in ENGLISH language 
                and maintain uniformity in the complete list of column type formulation for that column according to given values.
                Take the 2nd list of Colors as input list i give you and update list without any extra string
"""

Stats_Cleansing_Prompt = """
    **Task** :  the list values are of different age groups and your task is to change all the age that are below 1 or over 120 
                to the average(integer values) of the age in the given list excluding those.
                Take the input list i give you and update list without any extra string 
"""

Data_Enrichment_Prompt = """
    **Task** :  the list values are of different numbers and i want you to chnage the values in the list that are non numeric 
                to their respective numerical values.
                Take the input list i give you and update list without any extra string 
"""

Domain_Cleansing_Prompt ="""
    **Task** :  the list values are of different amount and your task is to change all the amounts that shows abnormality in 
                list with other values like if the amount is too high then replace to the average(integer values) of the amount in the given list excluding those.
                Take the input list i give you and update list without any extra string 
"""


def print_messages(recipient, messages, sender, config):
    # Print the message immediately
    print(
        f"Custom Response Sender: {sender.name} | Recipient: {recipient.name} "
    )
    # for message in messages:
    #     content = message.get("content", "")  # Get content or default to empty string
    #     print(f"{sender.name}: {content}")

    # if len(messages) > 1:  # Check if there are at least two messages
    #     second_message = messages[1]
    #     content = second_message.get("content", "")
    #     print(f"{sender.name}: {content}")

    socketio.emit(f'{sender.name}', f"Executing : {sender.name} ")
    time.sleep(4)
        # socketio.emit(f"{sender.name}", f"{content}")
    # print(f"Real Sender: {sender.last_speaker.name}")
    # assert sender.last_speaker.name in messages[-1].get("content")
    return False, None  # Required to ensure the agent communication flow continues

user_agent = ConversableAgent(
    name="User_Agent",
    system_message="Return the message as Input of message of agent called",
    llm_config=llm_config,
    max_consecutive_auto_reply=0,
    human_input_mode="NEVER",
)

# class Multi_Language_Cleansing_Agent(ConversableAgent):
#     """
#     A conversable agent designed for multi-language data cleansing.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Multi_Language_Cleansing_Agent".
#         system_message (str): The system message defining the agent's role and instructions.
#         llm_config (dict): Configuration for the language model.
#         human_input_mode (str): Specifies when the agent should ask for human input. Defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
multilanguage_conversion_agent = ConversableAgent(
    name="Multi_Language_Cleansing_Agent",
    system_message=Role+Multi_Language_Cleansing_Prompt +"Response should be a key value pair like dictionary with keys Data and count in which data will have the updated list and count will have the number of elements affected in the list ",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# class Stats_Cleansing_Agent(ConversableAgent):
#     """
#     A conversable agent focused on statistical data cleansing.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Stats_Cleansing_Agent".
#         system_message (str): The system message defining the agent's role and instructions.
#         llm_config (dict): Configuration for the language model.
#         human_input_mode (str): Specifies when the agent should ask for human input. Defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """

statistical_cleansing_agent = ConversableAgent(
    name="Stats_Cleansing_Agent",
    system_message=Role+Stats_Cleansing_Prompt +"Response should be just a list without any other string or any  python code",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# class Data_Enrichment_Agent(ConversableAgent):
#     """
#     A conversable agent designed for enriching data.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Data_Enrichment_Agent".
#         system_message (str): The system message defining the agent's role and instructions.
#         llm_config (dict): Configuration for the language model.
#         human_input_mode (str): Specifies when the agent should ask for human input. Defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
data_enrichment_agent = ConversableAgent(
    name="Data_Enrichment_Agent",
    system_message=Role+Data_Enrichment_Prompt +"Response should be just a list without any other string or any  python code",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# class Domain_Cleansing_Agent(ConversableAgent):
#     """
#     A conversable agent focused on cleansing data related to specific domains.
#
#     Args:
#         name (str): The name of the agent. Defaults to "Domain_Cleansing_Agent".
#         system_message (str): The system message defining the agent's role and instructions.
#         llm_config (dict): Configuration for the language model.
#         human_input_mode (str): Specifies when the agent should ask for human input. Defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
domain_cleansing_agent = ConversableAgent(
    name="Domain_Cleansing_Agent",
    system_message=Role+Domain_Cleansing_Prompt +"Response should be just a list without any other string or any python code",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# for agent in [user_agent, data_normalization_agent, multilanguage_conversion_agent,statistical_cleansing_agent,data_enrichment_agent,domain_cleansing_agent]:
#     agent.register_reply(
#         [ConversableAgent,], reply_func=print_messages, config=None
#     )

user_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    
    config={"callback": None},
)

data_normalization_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 

multilanguage_conversion_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
statistical_cleansing_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

data_enrichment_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
domain_cleansing_agent.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 


import json
import ast
import pandas as pd


def CleanseRows():
    df = pd.read_csv('static/DataFiles/Shopping_Survey_Raw.csv',low_memory=False)
    chat_results = user_agent.initiate_chats(
        [
            {
                "recipient": multilanguage_conversion_agent,
                "message": str(df['Color'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },
          
            {
                "recipient": data_normalization_agent,
                "message": str(df['Size'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },

          
            {
                "recipient": statistical_cleansing_agent,
                "message": str(df['Age'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": data_enrichment_agent,
                "message": str(df['ReviewRating'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": data_enrichment_agent,
                "message": str(df['PreviousPurchases'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": domain_cleansing_agent,
                "message": str(df['PurchaseAmountInUSD'].tolist()),
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            
        ]
    )

    # print("Multi_Language_Cleansing_Agent  Chat Summary: ", chat_results[0].summary)
    # df["Color"]=ast.literal_eval(chat_results[0].summary)
    # print("Data_Normalizing_Agent  Chat Summary: ", chat_results[1].summary)
    # df["Size"]=ast.literal_eval(chat_results[1].summary)
    # print("Stats_Cleansing_Agent  Chat Summary: ", chat_results[2].summary)
    # df["Age"]=ast.literal_eval(chat_results[2].summary)
    # print("Data_Enrichment_Agent  Chat Summary: ", chat_results[3].summary)
    # df["ReviewRating"]=ast.literal_eval(chat_results[3].summary)
    # print("Data_Enrichment_Agent2  Chat Summary: ", chat_results[4].summary)
    # df["PreviousPurchases"]=ast.literal_eval(chat_results[4].summary)
    # print("Domain_Cleansing_Agent  Chat Summary: ", chat_results[5].summary)
    # df["PurchaseAmountInUSD"]=ast.literal_eval(chat_results[5].summary)
    # df.to_csv('static/DataFiles//Shopping_Survey_Cleansed.csv', index=False)
    return {"message": "Working"}

