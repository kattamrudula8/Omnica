

# Import Statement
import datefinder
import mimetypes
import ntpath
import imaplib
import email
from email.header import decode_header
import datetime
import uuid
from pathlib import Path
import pathlib
import PyPDF2
import math
import datetime
import time
import os
import subprocess
import csv
from PIL import Image
import io
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from flask import jsonify
from flask import render_template, url_for, json, session
from flask_cors import CORS, cross_origin
from flask import Flask, request, send_file, send_from_directory
import shutil
import json
import h5py
# import numpy as np
from time import strptime
import pandas as pd
import logging
import re
# from datetime import datetime
import dill
import base64
import PIL
import PIL.Image
import ast
import psycopg2
import requests
from flask import redirect
import os
import sqlite3
# from bcrypt import hashpw, gensalt, checkpw
import papermill as pm
import uuid
import cv2
import numpy as np
#from socketio_setup import socketio
import google.generativeai as genai
import json
import requests
import speech_recognition as sr
import moviepy.editor as mp
from pydub import AudioSegment 
from pydub.silence import split_on_silence 
from datetime import datetime, timedelta
from collections import defaultdict 
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from codecarbon import track_emissions
from dotenv import load_dotenv
from dotenv import load_dotenv, find_dotenv
# from safety_check_agent import *
# import CleanseAgent as data_cleansing
# import devops_pipeline
import spacy
# from entity_ingestion import email_ingestion
import psycopg2
import os
from docx import Document
import glob
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from langchain_google_genai import ChatGoogleGenerativeAI
from bs4 import BeautifulSoup
from Agents.safety_check_agent import *
from Agents import CleanseAgent as data_cleansing 
from Agents import login_agent
from Agents import devops_pipeline
from Agents.entity_ingestion import entity_ingestion_snc
from Agents import ComplianceMultiAgent as compliance_assessment
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from pathlib import Path
from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Union, List
# from flask_socketio import SocketIO
# # import asyncio
# # from asyncio import WindowsSelectorEventLoopPolicy

# # asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

app = Flask(__name__)
# socketio = SocketIO(app)

from socket_io_setup import socketio
socketio.init_app(app, cors_allowed_origins="*")
# socketio = SocketIO(app, cors_allowed_origins="*", allow_EIO3=True)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['model'] = ""
app.config['mname'] = ""
app.config['vname'] = ""

# Create a global logger object
logger = logging.getLogger(__name__)

# Configure the logger to use Stackdriver Logging
# You can also set the logging level and format if needed
logging.basicConfig(level=logging.INFO)
# # creating logger
app.secret_key = os.urandom(24)  # Set a secret key for session management
workspace_dir_path = ""
workspace_org_path = "../Workspace/<USERNAME>/AccountWorkspace/"
_ = load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
AI_PROJECT_CONN_STR = os.environ['AI_PROJECT_CONN_STR']
genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
            "temperature":0.9,
            "top_p":1,
            "top_k":0,
            "max_output_tokens":4096
}


        
@app.route('/get_patient_file',methods = ['GET','POST'])
def get_patient_file():
    filePath = request.args.get("filePath")
    userName = request.args.get('userName')
    data_folder ="TicketData"
    global workspace_dir_path
    workspace_dir_path = workspace_org_path.replace("<USERNAME>",userName)+"Data/"+data_folder+"/"
    folder_path = workspace_dir_path
    file_obj = folder_path + filePath
    return send_file(file_obj)

@app.route("/get_patient_files_info")
def get_patient_files_info():
    data = []
    dbParams = json.loads(request.args.get("dbParams"))
    userName = dbParams['userName']
    folderName = dbParams['selectedPatient']
    folderName = folderName.strip()
    data_folder ="TicketData"
    global workspace_dir_path
    workspace_dir_path = workspace_org_path.replace("<USERNAME>",userName)+"Data/"+data_folder+"/"
    dir_path = workspace_dir_path+"/"+folderName
    summary_path =  workspace_org_path.replace("<USERNAME>",userName)+"/OutputCache/Summary/"+folderName+"/"
    columns = ["ID","FileName","Summary","FilePath","UserName"]
    i = 0
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.startswith(".")==False]
    print("Files",files)
    for l in files:
        # i = i+1
        l_path = Path(l) 
        if "TicketUpdate" not in str(l_path.stem):
            summary = ""
            if str(l_path.suffix) in [".pdf",".mp3",".mp4",".txt",".jpg",".jpeg",".png"]:
                summary_file_path = summary_path+l_path.stem+".txt"
                f = open(summary_file_path,'r')
                summary = json.loads(f.read())["text"]
                tcrow=[i,l_path.name,summary,folderName+"/"+l,userName]
                data.append(dict(zip(columns, tcrow)))
                i = i+1
    print(data)
    return json.dumps(data, indent=4) 

@app.route("/get_patient_files_list")
def get_patient_files_list():
    print("get_patient_files_list")
    
    try:
        data = []
        dbParams = json.loads(request.args.get("dbParams"))
        userName = dbParams['userName']
        folderName = dbParams['selectedPatient'].strip()
        data_folder = "TicketData"

        global workspace_dir_path
        workspace_dir_path = workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folderName)

        if not os.path.exists(dir_path):
            return jsonify({"status": "error", "message": f"Patient Directory {dir_path} not found"}), 404

        # Get list of files
        file_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

        # Prepare file data map
        file_data_map = {}

        for file_name in file_list:
            full_path = os.path.join(dir_path, file_name)
            file_ext = file_name.lower()

            try:
                if file_ext.endswith('.csv'):
                    file_data_map[file_name] = "CSV preview is not available."
                elif file_ext.endswith(('.txt', '.json', '.log', '.md')):
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    file_data_map[file_name] = content[:5000] + ("..." if len(content) > 5000 else "")
                else:
                    file_data_map[file_name] = None 
            except Exception as file_err:
                file_data_map[file_name] = f"Error reading file: {str(file_err)}"

        return jsonify({
            "status": "success",
            "folder": folderName,
            "files": file_list,
            "data_on_file": file_data_map
        })

    except Exception as exec:
        return jsonify({"status": "error", "message": str(exec)}), 500

@app.route("/save_summary_with_selected_topics", methods = ['GET','POST'])
def save_summary_with_selected_topics():
    print("save_summary_with_selected_topics")

    try:
        dbParams = request.get_json()
        print(dbParams)

        userName = dbParams.get("userName")
        folderName = dbParams.get("selectedPatient", "").strip()
        file_name = dbParams.get("selectedFileName")
        summary_data = dbParams.get("summaryData")

        if not all([userName, folderName, file_name, summary_data]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Build path
        data_folder = "TicketData"
        workspace_dir_path = workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folderName)
        full_file_path = os.path.join(dir_path, file_name)
        fileAbs = Path(full_file_path)
        
        filename = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Summary/{folderName}/{fileAbs.stem}.txt"
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        out_obj = {"input_tokens":0,"output_tokens":0,"text":summary_data}
        with open(filename,"w") as f:
            f.write(json.dumps(out_obj))
        return jsonify({"status": "success", "message": "Success"}), 200

    except Exception as exec:
        print(str(exec))
        return jsonify({"status": "error", "message": str(exec)}), 500

@app.route("/gemini_query_file_question", methods=["GET"])
def gemini_query_file_question():
    print("gemini_query_file_question")

    try:
        dbParams = json.loads(request.args.get("dbParams"))
        print(dbParams)

        userName = dbParams.get("userName")
        folderName = dbParams.get("selectedPatient", "").strip()
        file_name = dbParams.get("selectedFileName")
        user_query = dbParams.get("userQuery")

        print(userName, folderName, file_name, user_query)
        if not all([userName, folderName, file_name, user_query]):
            return "Missing required parameters", 400

        data_folder = "TicketData"
        workspace_dir_path = workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folderName)
        full_file_path = os.path.join(dir_path, file_name)

        if not os.path.exists(full_file_path):
            return f"File not found at {full_file_path}", 404

        print(f"User Query: {user_query}")

        # Construct prompt
        prompt = (
            f"Based on the contents of the uploaded file, answer this question:\n\n"
            f"{user_query}\n\n"
            f"Your response should be clear and context-aware."
        )

        # Run Gemini processing
        response = analyze_content_with_gemini(full_file_path, prompt)

        if response:
            return f"<b>Q:</b> {user_query}<br><br><b>A:</b> {response}", 200
        else:
            return "Gemini returned no response", 500

    except Exception as e:
        print(f"Exception: {e}")
        return str(e), 500



# Configure a route to handle the request for displaying the models
@app.errorhandler(500)
def handle_internal_server_error(e):
    response = jsonify(error=str(e))
    response.status_code = 500
    return response

# Configure a route to handle the request for displaying the models


@app.errorhandler(500)
def handle_internal_server_error(e):
    response = jsonify(error=str(e))
    response.status_code = 500
    return response


@app.route("/favicon.ico")
def favicon():
    return send_file(os.path.join(app.static_folder, "CDN/images/entity.jpg"))


@app.route('/EntityComplianceAction')
def EntityComplianceAction():
    selectedId = request.args.get("id")
    return render_template('EntityComplianceAction.html',ticketId=selectedId)



@app.route("/get_patient_folders")
#@track_emissions(output_dir="static",project_name="Panacea") 
def get_patient_folders():
    data = []
    dbParams = json.loads(request.args.get("dbParams"))
    data_folder ="TicketData"
    global workspace_dir_path
    workspace_dir_path = workspace_org_path+data_folder+"/"
    dir_path = workspace_dir_path
    print(dir_path)
    columns = ["name"]
    for l in os.listdir(dir_path):
        tcrow=[l]
        data.append(dict(zip(columns, tcrow)))
    print(data)
    return json.dumps(data, indent=4) 

    
"""Gemini"""
def gemini_summary(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "summarize the below report in 6 points numbered list maximum \n\n" + entity_report
    response = model.generate_content(prompt)
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-SummaryContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print("gemini_summary done")
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

def timeline_scores(entity_report):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = """Identify all the different dates in all content in below. List the Important Events in json format with keys as EventDate,EventType,EventDescription, Sentiment,SentimentScore based on the below report. 
    Return response in form of json array without any additional text. 
    
    Provide the Sentiment any of the  options: ['POSITIVE','NEGATIVE','NEUTRAL']
    \n\n""" + entity_report
    response = model.generate_content(prompt)
    #Displays the response
    timeline = response.candidates[0].content.parts[0].text
    print(timeline)
    return timeline

def gemini_sentiment(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "provide the sentiment of  below report in any of the below options: POSITIVE,NEGATIVE,NEUTRAL. Return answer in form of json with key as Sentiment and any one value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-SentimentContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print("gemini_sentiment done")
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 6:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 6:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

def gemini_risk(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "provide the risk level of  below report in any of the below options: HIGH, MEDIUM, LOW. Return answer in form of json with key as Risk and any one value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-RiskContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print("gemini_risk done")
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 6:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 6:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

def gemini_compliance(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "provide the compliance level of  below report in any of the below options: HIGH, MEDIUM, LOW. Return answer in form of json with key as Compliance and any one value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-ComplianceContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print("gemini_compliance done")
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 6:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 6:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

#NER using spacy
def spacy_NER(patient_report):
    # Load the English model
    nlp = spacy.load("en_core_web_sm")
    # Process the text using the SpaCy model
    doc = nlp(patient_report)
    # Extract entities with specific labels
    selected_entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['PERSON', 'GPE', 'ORG', 'DATE']]
    # Group entities by label
    grouped_entities = {}
    for entity, label in selected_entities:
        if label not in grouped_entities:
            grouped_entities[label] = []
        grouped_entities[label].append(entity)
    # Create a formatted string
    formatted_string = {}
    for label, entities in grouped_entities.items():
        # formatted_string += f"{label}: {', '.join(entities)}\n\n"
        formatted_string[label] = entities
    return formatted_string

def gemini_NER(entity_report, reportName, domainName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    # prompt = "provide the Named Entities such as hospital names, patient names, doctor names,locations,medication names, and dates mentioned in the patient report as json key value pairs \n\n" + entity_report
    # prompt = "provide the named entities such as who are the people involved, locations involved, datestamps, items or servers involved as json key value pairs \n\n"+ entity_report
    prompt = ""
    if domainName == "Clinical":
        prompt = "provide the Named Entities such as hospital names, patient names, doctor names,locations,medication names, and dates mentioned in the patient report as json key value pairs \n\n" + entity_report
    elif domainName == "Incidents":
        prompt = "provide the named entities such as who are the people involved, locations involved, dates involved, items or servers involved as json key value pairs \n\n" + entity_report
    elif domainName == "Manufacturing":
        prompt = "provide the named entities such as who are the people involved, locations involved, dates involved, items or products involved, costs involved as json key value pairs \n\n" + entity_report
    elif domainName == "Gas Supply":
        prompt = "provide the named entities such as who are the people involved, locations involved, dates involved, items involved, costs involved as json key value pairs \n\n" + entity_report
    elif domainName == "Cyber Security":
        prompt = "provide the named entities such as who are the people involved, locations involved, dates involved, risks and penalties involved, costs involved as json key value pairs \n\n" + entity_report
    else:
        prompt = "provide the named entities such as hospital names, patient names, doctor names,locations,medication names, and dates mentioned in the patient report as json key value pairs  \n\n" + entity_report
    response = model.generate_content(prompt)
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-NERContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    print("gemini_NER done")
    # print(json.dumps(response))

    # Three PArameters - Response, OpenAI, NERContent.txt - FileName - OpenAI-NERContent.txt
    # Three PArameters - Response, Gemini, Sentiment.txt - FileName - Gemini-Sentiment.txt

    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_emotion(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Predict the emotion based on report from provided options : [ 'HAPPINESS', 'SADNESS', 'ANGER', 'FEAR', 'SURPSRISE', 'DISGUST']. Return answer in form of json with key as Emotion and value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    print("gemini_emotion done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-EmotionContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 1:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 1:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_tone(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Predict the Tone based on report from provided options : [ 'FORMAL', 'INFORMAL', 'OPTIMISTIC', 'HARSH']. Return answer in form of json with key as Tone and any one value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    print("gemini_tone done")
    cache_file_path =workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-ToneContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 1:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 1:
            f = open(cache_file_path, encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_englishmaturity(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Predict the English Maturity of the report from provided options : [ 'AVERAGE', 'MEDIUM', 'PROFICIENT', 'LOW']. Return answer in form of json with key as EnglishMaturity and value from given options.\n\n" + entity_report
    response = model.generate_content(prompt)
    print("gemini_englishmaturity done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-EngmatContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 1:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 1:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_determine_sentiment_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the sentiment of the report. Return answer in form of json with key as SentimentWords and value as list of identified words or phrases."
    response = model.generate_content(prompt)
    print("gemini_sentiment_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-SentHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

def gemini_determine_risk_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the risk level of the report. Return answer in form of json with key as RiskWords and value as list of identified words or phrases."
    response = model.generate_content(prompt)
    print("gemini_risk_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-RiskHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()

def gemini_determine_compliance_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the compliance level of the report. Return answer in form of json with key as ComplianceWords and value as list of identified words or phrases."
    response = model.generate_content(prompt)
    print("gemini_compliance_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-CompHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(
            cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_determine_tone_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the tone of the report. Return answer in form of json with key as ToneWords and value as list of identified words or phrases"
    response = model.generate_content(prompt)
    print("gemini_tone_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-ToneHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_determine_emotion_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the emotion of the report. Return answer in form of json with key as EmotionWords and value as list of identified words or phrases"
    response = model.generate_content(prompt)
    print("gemini_emotion_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-EmoHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(
                cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()


def gemini_determine_englishmaturity_highlights(entity_report, reportName,userName):
    entity = reportName.split('/')
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = "Given a Report \n\n" + entity_report + \
        "\n\n Provide the key words or phrases that strongly contribute to determining the English Maturity of the report. Return answer in form of json with key as EngMatWords and value as list of identified words or phrases"
    response = model.generate_content(prompt)
    print("gemini_englishmaturity_highlights done")
    cache_file_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Gemini-EngmatHighContent-{entity[0]}.txt"
    path = Path(cache_file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        returnData = response.candidates[0].content.parts[0].text
        if len(returnData) > 10:
            f = open(cache_file_path
                , "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.candidates[0].content.parts[0].text

    except:
        returnData = response.text
        if len(returnData) > 10:
            f = open(cache_file_path, "w", encoding='cp1252')
            f.write(returnData)
            f.close()
        return response.text
    finally:
        # open and read the file after the overwriting:
        f = open(cache_file_path, "r", encoding='cp1252')
        return f.read()

@app.route("/get_valid_rag_queries")
#@track_emissions(output_dir="static",project_name="Panacea")
def get_valid_rag_queries():
    app_name = request.args.get("app")
    queries = []
    if app_name == "Panacea":
        queries = ["What are the medicines prescribed?","When is the patient registered?"]
    elif app_name == "Sentinel":
        queries = ["What are the companies mentioned?"]
    return queries

def create_rag_model():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest",
                                   temperature=0.3)

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain


def create_vector_db(patient_report):
    # code to extract text from folder files
    text = patient_report
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=256, chunk_overlap=20)
    text_chunks = text_splitter.split_text(text)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    
@app.route("/create_search_query")
#@track_emissions(output_dir="static",project_name="Panacea")
def create_search_query():
    dbParams = json.loads(request.args.get("dbParams"))
    reportName = "RAG"
    user_question = dbParams['userQuestion']
    rag_db_name = dbParams['ragDbName']
    userName = dbParams['userName']
    entity = reportName.split('_')
    print(dbParams)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("../VectorDB/"+rag_db_name, embeddings,allow_dangerous_deserialization =True)
    print("db loaded")
    docs = new_db.similarity_search(user_question)
    print("docs searched")
    chain = create_rag_model()
    print("rag model created")

    try:
        response = chain(
            {"input_documents": docs, "question": user_question}, return_only_outputs=True)
        if response:
            f = open(
                workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/RAG/Gemini-RAG-{entity[0]}.txt", "w", encoding='utf-8')
            f.write(json.dumps(response))
            f.close()
        return response
    except:
        f = open(
            workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/RAG/Gemini-RAG-{entity[0]}.txt", "r", encoding='utf-8')
        return f.read()
 
@app.route("/gemini_results")
#@track_emissions(output_dir="static",project_name="Panacea")
def gemini_results():
    dbParams = json.loads(request.args.get("dbParams"))
    # domainName = dbParams['domainName']
    userName = dbParams['userName']
    data_folder ="TicketData"
    global workspace_dir_path
    workspace_dir_path = workspace_org_path.replace("<USERNAME>",userName)+"Data/"+data_folder+"/"
    workspace_path = workspace_dir_path
    print(workspace_path)
    folder = dbParams['selectedPatient']
    folder = folder.strip()
    folder_path = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Summary/{folder}"
    print(folder_path)
    filesList = [folder_path+"/"+str(filepath) for filepath in os.listdir(folder_path)]
    print(filesList)
    reportName = filesList[0]
    print(dbParams)
    print(reportName)
    input_tokens = 0
    output_tokens = 0
    entity_report = ""
    timeline = []
    for file in filesList:
        fileAbs = Path(file)
        # file = Path(workspace_path+"/"+file)
        # filename = workspace_org_path.replace("<USERNAME>",userName)+f"OutputCache/Summary/{fileAbs.parent}/{fileAbs.stem}.txt"
        # print(filename)
        if "TicketUpdate.txt" not in str(file):
            # if fileAbs.suffix in [".pdf",".mp3",".mp4"]:
            f = open(file, "r", encoding='utf-8')
            summary = f.read()
            # input_tokens += summary_obj["input_tokens"]
            # output_tokens += summary_obj["output_tokens"]
            # create_timestamp = file.stat().st_ctime
            # create_time = datetime.fromtimestamp(create_timestamp)
            # timeline.append({"Event Type":fileAbs.stem,"Event Description":summary,"Time":create_time})
            entity_report += summary + "\n\n"
    # print(entity_report)
    timeline_data = timeline_scores(entity_report)
    output_json = {
        "completeReport": entity_report,
        "Summary": gemini_summary(entity_report, reportName,userName),
        "Sentiment": gemini_sentiment(entity_report, reportName,userName),
        # "NER": gemini_NER(entity_report, reportName, domainName),
        "Emotion": gemini_emotion(entity_report, reportName,userName),
        "Tone": gemini_tone(entity_report, reportName,userName),
        # "Risk": gemini_risk(entity_report, reportName,userName),
        # "Compliance": gemini_compliance(entity_report, reportName,userName),
        "EnglishMaturity": gemini_englishmaturity(entity_report, reportName,userName),
        "SentimentWords": gemini_determine_sentiment_highlights(entity_report, reportName,userName),
        "EmotionWords": gemini_determine_emotion_highlights(entity_report, reportName,userName),
        "ToneWords": gemini_determine_tone_highlights(entity_report, reportName,userName),
        "EngMatWords": gemini_determine_englishmaturity_highlights(entity_report, reportName,userName),
        # "RiskWords": gemini_determine_risk_highlights(entity_report, reportName,userName),
        # "ComplianceWords": gemini_determine_compliance_highlights(entity_report, reportName,userName),
        "Timeline": timeline_data,
        "InputTokens": input_tokens,
        "OutputTokens": output_tokens,
        "SentimentScores":timeline_data,
        "fivewh":get_fivewh_analysis(folder_path)
    }
    # output_json = {
    #     "NER":spacy_NER(entity_report),
    #     "fivewh":get_fivewh_analysis(folder_path)
    # }
    return output_json


def summary_msg(msg):
    # Set your gemini API key
    
    # cleaning text
    msg = re.sub(r"\n+", " ", msg)
    msg = re.sub(r"\s+", " ", msg)
    # Set the parameters for the GPT-3 API request
    prompt = "Summarization of Support Case :\n" + msg
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", generation_config=generation_config)
 
    response = model.generate_content(prompt)
    summary = response.text
    return summary

def gemini_detect_location(msg):
    # Set your gemini API key
    
    # cleaning text
    msg = re.sub(r"\n+", " ", msg)
    msg = re.sub(r"\s+", " ", msg)
    # Set the parameters for the GPT-3 API request
    prompt = "Provide the Loaction names in the given email body :\n" + msg + "\n Dont Provide any extra information"
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", generation_config=generation_config)
 
    response = model.generate_content(prompt)
    locations = response.text
    return locations
 
def detect_sender_address(msg):
    try:
        
        pattern = r"client-ip=(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        matches = re.findall(pattern, msg)
        ip_address = matches[0]
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url)
        data = response.json()
    
        if data["status"] == "success":
            city = data["city"]
            region = data["regionName"]
            country = data["country"]
            return city + "," + region + "," + country
        else:
            return "NA"
    except:
        return "Unable to retrieve IP"
 
def gemini_detect_persons(msg):
    # Set your gemini API key
    
    # cleaning text
    msg = re.sub(r"\n+", " ", msg)
    msg = re.sub(r"\s+", " ", msg)
    # Set the parameters for the GPT-3 API request
    prompt = "Provide the Persons names in the given email body :\n" + msg
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", generation_config=generation_config)
 
    response = model.generate_content(prompt)
    persons = response.text
    return persons

def detect_date_time(msg):
    date_time = []
    matches = datefinder.find_dates(msg)
    for match in matches:
        if match not in date_time:
            date_time.append(
                "%s" % (str(match.strftime("%a, %d %b %Y %H:%M:%S"))))
    return ",".join(date_time)
  
def detect_days(msg):
    date_time = []
    matches = datefinder.find_dates(msg)
    for match in matches:
        if match not in date_time:
            date_time.append(
                "%s" % (str(match.strftime("%a, %d %b %Y %H:%M:%S"))))
    return date_time


def get_fivewh_analysis(folder_path):
    email_data = ""
    with open(folder_path+"/Amy_Cripto_EncounterDetails.txt","r",encoding='UTF-8') as f:
        email_data = f.read()
    email_message = email.message_from_string(email_data)
    date_tuple = email.utils.parsedate_tz(email_message['Date'])
    sender_name, sender_email = email.utils.parseaddr(
        email_message['From'])
    local_message_date = ""
    if date_tuple:
        # email recived date
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        local_message_date = "%s" % (
            str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
    dates = detect_days(email_data)
    # dates = ['Tue, 28 Mar 2023 00:00:00', 'Wed, 01 Mar 2023 00:00:00', 'Thu, 02 Mar 2023 00:00:00', 'Fri, 03 Mar 2023 00:00:00', 'Sat, 04 Mar 2023 00:00:00', 'Wed, 03 May 2023 09:14:00']
    
    # Convert the dates to datetime objects
    date_objects = [datetime.strptime(
        date, '%a, %d %b %Y %H:%M:%S') for date in dates]
    
    # Find the oldest and latest dates
    if date_objects: 
        oldest_date = min(date_objects)
        latest_date = max(date_objects)
        # Calculate the number of days between the two dates
        days_diff = (latest_date - oldest_date).days
        output = f"The oldest date is {oldest_date.strftime('%Y-%m-%d')}, " + f"The latest date is {latest_date.strftime('%Y-%m-%d')}, " + \
            f"The number of days between the two dates is {days_diff} days"
    else:
        output = "No Dates Found"
    Case_summary = summary_msg(email_data)
    Case_locations = gemini_detect_location(email_data)
    email_message = email_message
    sender_address = detect_sender_address(email_message["Received-SPF"])
    Case_persons = gemini_detect_persons(email_data)
    sender_email = sender_email
    sender_name = sender_name
    Case_date_time = detect_date_time(email_data)
    local_message_date = local_message_date
    mail_recevied_date = local_message_date
    sla = "8 hours"
    impact = "High"
    analysis_obj = {
        "S#": ["1", "2a", "2b", "3a", "3b", "3c", "4a", "4b", "4c", "5", "6", "7"],
        "investigation": ["What", "Where", "Where", "Who", "Who", "who", "When", "When", "when", "Why", "SLA", "Impact"],
        "Algorithm": ["gpt-4o-mini", "gpt-4o-mini", "Spatial Extraction", "gpt-4o-mini", "Master data", "SenderEmail & SenderName", "datefinder", "Imaplib", "LatestDate, OldestDate, No.Of Days", "NA", "gpt-4o-mini", "gpt-4o-mini"],
        "Value": [Case_summary, Case_locations, sender_address, Case_persons, "NA", sender_email + " & " + sender_name, Case_date_time, mail_recevied_date, output, "NA", sla, impact]
    }
    return analysis_obj

@app.route("/start_chat")
def start_chat():
#   print(request.args.get("dbParams"))
  dbParams = json.loads(request.args.get("dbParams"))
  query = dbParams["query"]
  app_name = dbParams["appName"]
  user_proxy.initiate_chat(groupchat_manager, message=app_name.upper() + " - " +query)
  messages = user_proxy.chat_messages[groupchat_manager]
  return jsonify(messages)

@app.route("/CleanseRows")
def CleanseRows():
  data_cleansing.CleanseRows()
#   socketio.emit('mainmessage', f"Custom Response Sender: From Main File | Recipient: HTMl ")
  return {"Message":"Working"}


@app.route("/EntityAICleansing")
def EntityAICleansing():  
  return render_template('EntityAICleansing.html')


@app.route('/get_csv_files')
def get_csv_files():
    species_dir = 'static/MedicalCodes'  # Replace with the actual path to your 'species' folder
    csv_files = [f for f in os.listdir(species_dir) if f.endswith('.csv')]
    return jsonify({'csv_files': csv_files})

@app.route('/get_csv_data', methods=['POST'])
def get_csv_data():
    selected_file = request.form['csv_file']
    file_path = os.path.join('static/MedicalCodes/', selected_file) 
    try:
        df = pd.read_csv(file_path)
        # Convert DataFrame to a list of dictionaries
        data = df.to_dict('records')
        columns = list(df.columns)
        return jsonify({'data': data, 'columns': columns})
    except FileNotFoundError:
        return jsonify({'error': 'File not found.'})


@app.route("/EntityAttachmentSummaryAction")
def EntityAttachmentSummaryAction():
  selectedId = request.args.get("id")
  userName = request.args.get("userName")
  data_folder ="TicketData"
  global workspace_dir_path
  workspace_dir_path = workspace_org_path.replace("<USERNAME>",userName)+"Data/"+data_folder+"/"
  print(workspace_dir_path)
  return render_template('EntityAttachmentSummaryAction.html', ticketId=selectedId)

@app.route("/EntitySummaryAction")
def EntitySummaryAction():
  selectedId = request.args.get("id")
  userName = request.args.get("userName")
#   tickets_file_path = '../Data/AutoTicket/KnowledgeBase_questions.json'
#   with open(tickets_file_path,'r') as tf:
#     tickets = json.load(tf)
#   text = tickets[selectedId]
  data_folder ="TicketData"
  global workspace_dir_path
  workspace_dir_path = workspace_org_path.replace("<USERNAME>",userName)+"Data/"+data_folder+"/"
  print(workspace_dir_path)
  return render_template('EntitySummaryAction.html',ticketId=selectedId)


@app.route("/EntitiesList")
def EntitiesList():    
  return render_template('EntitiesList.html')  
    

@app.route("/get_entities")
def get_entities():
    entities = []
    try:
        connection = psycopg2.connect(
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            dbname = os.getenv('DB_NAME'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM "Entities"."Entity"')
        columns = [desc[0] for desc in cursor.description]
        records = cursor.fetchall()
        for record in records:
            tcrow = [str(rowval) for rowval in record]
            entities.append(dict(zip(columns, tcrow)))
    except Exception as exc:
        print(exc)
    return entities

@app.route("/get_entity_attachments")
def get_entity_attachments():
    entity_id= request.args.get("EntityId")
    entity_attachments = []
    try:
        connection = psycopg2.connect(
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            dbname = os.getenv('DB_NAME'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )
        cursor = connection.cursor()
        cursor.execute(f'''SELECT * FROM "Entities"."EntityAttachments" WHERE "EntityId" = '{entity_id}' ''')
        columns = [desc[0] for desc in cursor.description]
        records = cursor.fetchall()
        for record in records:
            tcrow = [str(rowval) for rowval in record]
            entity_attachments.append(dict(zip(columns, tcrow)))
    except Exception as exc:
        print(exc)
    cursor.close()
    connection.close()
    return entity_attachments

@app.route('/get_images')
def get_images():
    image_files = []
    # userName = request.args.get("userName")
    # images_path = workspace_org_path.replace("<USERNAME>",userName)+"OutputCache/tempShots"
    for filename in os.listdir("static/tempShots"):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(filename)
    return '\n'.join(image_files)  

@app.route("/get_action_entity")
def get_action_entity():
    query = request.args.get("query")
    # print("_"+selectedId)
    entities = []
    try:
        connection = psycopg2.connect(
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            dbname = os.getenv('DB_NAME'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT')
        )
        cursor = connection.cursor()
        # query='SELECT "Title","Content" FROM "Entities"."Entity" WHERE "EntityId" ='+"'"+selectedId+"'"
        print(query)
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        records = cursor.fetchall()
        for record in records:
            tcrow = [str(rowval) for rowval in record]
            entities.append(dict(zip(columns, tcrow)))
    except Exception as exc:
        print(exc)
    cursor.close()
    connection.close()
    return entities


@app.route("/InsuranceService")
def insuranceservice():
    dbParams = json.loads(request.args.get("dbParams"))
    dataPrompt = dbParams['dataprompt']
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=AI_PROJECT_CONN_STR)

    agent = project_client.agents.get_agent("asst_2XovUvdD1G2ZW0uyh8sgMtjF")

    thread = project_client.agents.create_thread()

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        # content="I have chroncic arithrities in left leg. Can u suggest health insurance policies"
        content=dataPrompt
    )

    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id)
    messages = project_client.agents.list_messages(thread_id=thread.id)
    response = []
    for text_message in messages.text_messages:
        response.append(text_message.as_dict())
    return_dict= response[0]["text"]["value"].replace("```json","").replace("```","")
    return ast.literal_eval(return_dict)


@app.route("/TimelineSentimentAnalysis")
def TimelineSentimentAnalysis():
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=AI_PROJECT_CONN_STR)

    agent = project_client.agents.get_agent("asst_lA64IHKT2H04DNQnAyktYIBO")

    thread = project_client.agents.create_thread()

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="**Initial sales report request:** On January 20, 2025, Katherine Rose requested weekly sales data for specific products to be sent to her email address.\n\n**Follow up on sales report request:**  On January 23, 2025, Katherine followed up because she hadn't received the requested data.\n\n**Incomplete data report:** On January 28, 2025, Katherine reported that the received data was incomplete, specifically missing information for the previous week.\n\n**Confirmation of corrected data:** On February 3, 2025, Katherine confirmed that the corrected data had been received and was accurate.\n"
    )

    run = project_client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent.id)
    messages = project_client.agents.list_messages(thread_id=thread.id)
    response = []
    for text_message in messages.text_messages:
        response.append(text_message.as_dict())
    
    timeline_response = response[0]
    with open("static/sentiment_scores.txt","w") as f:
            f.write(json.dumps(timeline_response))
    # Upload a file and add it to the client 
    file = project_client.agents.upload_file_and_poll(
        file_path="static/sentiment_scores.txt", purpose=FilePurpose.AGENTS
    )
    print(f"Uploaded file, file ID: {file.id}")
    code_interpreter = CodeInterpreterTool(file_ids=[file.id])
    # create agent with code interpreter tool and tools_resources
    ci_agent = project_client.agents.create_agent(
        model="omnica-gpt-4o",
        name="Sentiment_Renderer",
        instructions="You are helpful assistant",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    # create a thread
    ci_thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {ci_thread.id}")

    # create a message
    ci_message = project_client.agents.create_message(
        thread_id=ci_thread.id,
        role="user",
        content="Render line chart by analysing the input file with EventDate on x-axis and SentimentScore on y-axis and provide file to me",
    )
    print(f"Created message, message ID: {ci_message.id}")

    # create and execute a run
    run = project_client.agents.create_and_process_run(thread_id=ci_thread.id, agent_id=ci_agent.id)
    print(f"Run finished with status: {run.status}")

   
    # delete the original file from the agent to free up space (note: this does not delete your version of the file)
    project_client.agents.delete_file(file.id)
    print("Deleted file")
    ci_messages = project_client.agents.list_messages(thread_id=ci_thread.id) 
    # save the newly created file
    for text_message in ci_messages.text_messages:
        print(text_message)

    for image_content in ci_messages.image_contents:
        print(f"Image File ID: {image_content.image_file.file_id}")
        file_name = f"{image_content.image_file.file_id}_image_file.png"
        project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
        print(f"Saved image file to: {Path.cwd() / file_name}") 
    
    project_client.agents.delete_agent(ci_agent.id)
    return response[0]

if __name__ == '__main__':
    # app.run(debug=True,port=5005)
    # mlflow_process.terminate()
    app.run(host='0.0.0.0',port=5005,debug=True)
    # socketio.run(app,port=5005,debug=True)
