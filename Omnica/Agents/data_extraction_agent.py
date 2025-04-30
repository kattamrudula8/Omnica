import os
import re
import moviepy.editor as mp
from pydub import AudioSegment 
from pathlib import Path
import speech_recognition as sr

import PyPDF2
from autogen import ConversableAgent
import google.generativeai as genai
import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # Load from .env file if it exists


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

generation_config = {
            "temperature":0.9,
            "top_p":1,
            "top_k":0,
            "max_output_tokens":4096
        }
safety_settings = [
{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
},
{
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
},
{
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
},
{
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
},
]
genai.configure(api_key=GOOGLE_API_KEY)  # This is the correct way

model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)
if os.path.exists("PatientSummary.txt"):
    os.remove("PatientSummary.txt")

# LLM Configurations
config_list = [{'model': 'gemini-1.5-flash', 'api_key': GOOGLE_API_KEY, "api_type": "google"}]
groq_config_list = [
    {
        "api_type": "groq",
        "model": "llama3-8b-8192",
        "api_key": GROQ_API_KEY,
        
    }
]
llm_config = {
    "cache_seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}
groq_llm_config = {
    "cache_seed": 42,
    "temperature": 0,
    "config_list": groq_config_list,
    "timeout": 120,
}

user_agent = ConversableAgent(
    name="User_Agent",
    system_message="Return the same message as Input",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# class Pdf2Text_Conversion_Agent(ConversableAgent):
#     """
#     A conversable agent designed to convert PDF files to text by executing the 'pdf_to_text' function.
#
#     Args:
#         name (str): The name of the agent, defaults to "Pdf2Text_Conversion_Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'pdf_to_text'.
#         llm_config (dict): Language model configuration.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
pdf2text_conversion_agent = ConversableAgent(
    name="Pdf2Text_Conversion_Agent",
    system_message="You should execute function pdf_to_text with the input",
    llm_config=groq_llm_config,
    human_input_mode="NEVER",
)

# class Video2Text_Conversion_Agent(ConversableAgent):
#     """
#     A conversable agent designed to convert video files to text by executing the 'video_to_text' function.
#
#     Args:
#         name (str): The name of the agent, defaults to "Video2Text_Conversion_Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'video_to_text'.
#         llm_config (dict): Language model configuration.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
video2text_conversion_agent = ConversableAgent(
    name="Video2Text_Conversion_Agent",
    system_message="You should execute function video_to_text with the input",
    llm_config=groq_llm_config,
    human_input_mode="NEVER",
)

# class Audio2Text_Conversion_Agent(ConversableAgent):
#     """
#     A conversable agent designed to convert audio files to text by executing the 'audio_to_text' function.
#
#     Args:
#         name (str): The name of the agent, defaults to "Audio2Text_Conversion_Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'audio_to_text'.
#         llm_config (dict): Language model configuration.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
audio2text_conversion_agent = ConversableAgent(
    name="Audio2Text_Conversion_Agent",
    system_message="You should execute function audio_to_text with the input",
    llm_config=groq_llm_config,
    human_input_mode="NEVER",
)

# class Image2Text_Conversion_Agent(ConversableAgent):
#     """
#     A conversable agent designed to convert images to text by executing the 'image_to_text' function.
#
#     Args:
#         name (str): The name of the agent, defaults to "Image2Text_Conversion_Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'image_to_text'.
#         llm_config (dict): Language model configuration.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
image2text_conversion_agent = ConversableAgent(
    name="Image2Text_Conversion_Agent",
    system_message="You should execute function image_to_text with the input",
    llm_config=groq_llm_config,
    human_input_mode="NEVER",
)

# class Summary_Generating_Agent(ConversableAgent):
#     """
#     A conversable agent designed to generate summaries of text by executing the 'summarytext' function.
#
#     Args:
#         name (str): The name of the agent, defaults to "Summary_Generating_Agent".
#         system_message (str): Instructions for the agent, specifying the execution of 'summarytext'.
#         llm_config (dict): Language model configuration.
#         human_input_mode (str): Specifies when human input is required, defaults to "NEVER".
#
#     @version 1.0.2
#     @author Ajay
#     """
summary_generating_agent = ConversableAgent(
    name="Summary_Generating_Agent",
    system_message="You should execute function summarytext with the input",
    llm_config=groq_llm_config,
    human_input_mode="NEVER",
)


def write_summary(text):
    system_prompt = """
                            You are an expert in making report and you have to provide the summary of thre below report
                            """
                    
    user_prompt = "Provide the short summary on this in less tha 100 words"
    input_prompt= [system_prompt,text, user_prompt]
    response = model.generate_content(input_prompt)
    with open('PatientSummary.txt', "a", encoding="utf-8") as file:
        file.write(response.text+"\n")  

@user_agent.register_for_execution()
@summary_generating_agent.register_for_llm(description="You should execute the function")
def summarytext(message:str) -> str:
    # print()
    try:
        with open(message, 'r', encoding='utf-8') as file:
            file_content = file.read()
        print(file_content)
        return file_content
    except FileNotFoundError:
        return f"Error: File not found at {message}"
    except Exception as e:
        return f"An error occurred: {e}"
    

@user_agent.register_for_execution()
@pdf2text_conversion_agent.register_for_llm(description="You should execute the function")
def pdf_to_text(message:str) -> str:
    # print()
    for root, dirs, files in os.walk(message):
        # Calculate relative path from source to current directory
        relative_path = os.path.relpath(root, message)

        # Create corresponding directory structure in destination
        dest_path = os.path.join("ExtractedFiles", relative_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_filepath = os.path.join(root, file)
                filename_without_ext, _ = os.path.splitext(file)
                output_filename = os.path.join(dest_path, f"{filename_without_ext}.txt")

                try:
                    # with open(output_filename, "w", encoding="utf-8") as outfile:
                    #     outfile.write(pdf_filepath)  # Write the full path
                    # print(f"Saved PDF path to: {output_filename}")
                    pdf_file = open(pdf_filepath, 'rb')
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text_content = ' '
                    for page_number in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_number]
                        text_content += page.extract_text()
                    pdf_file.close()
                    text_content = re.sub(r'\s+', ' ', text_content)
                    
                except Exception as e:
                    print(f"Error saving file: {e}") 
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(text_content)     
    print("PDF Extracted")
    write_summary(text_content)    
    return text_content

@user_agent.register_for_execution()
@image2text_conversion_agent.register_for_llm(description="You should execute the function")
def image_to_text(message:str) -> str:
    # print()
    for root, dirs, files in os.walk(message):
        # Calculate relative path from source to current directory
        relative_path = os.path.relpath(root, message)

        # Create corresponding directory structure in destination
        dest_path = os.path.join("ExtractedFiles", relative_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            if file.lower().endswith(".png") or file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
                image_filepath = os.path.join(root, file)
                filename_without_ext, _ = os.path.splitext(file)
                output_filename = os.path.join(dest_path, f"{filename_without_ext}.txt")

                try:
                    # with open(output_filename, "w", encoding="utf-8") as outfile:
                    #     outfile.write(pdf_filepath)  # Write the full path
                    # print(f"Saved PDF path to: {output_filename}")
                    file = Path(image_filepath)
                    image_parts = [
                    {
                        "mime_type": "image/jpeg", ## Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
                        "data": file.read_bytes()
                    }
                    ]
                    system_prompt = """
                            You are a radiologist expert in interpreting MRI scanning reports and identifies abnormalities to provide accurate diagnoses..
                            Input images in the form of MRI sacnning images  will be provided to you,
                            and your task is to respond to questions based on the image.
                            """
                    
                    user_prompt = "What specific abnormalities or findings were identified in the MRI brain scan image?"
                    input_prompt= [system_prompt, image_parts[0], user_prompt]
                    response = model.generate_content(input_prompt)
                    input_tokens = response.usage_metadata.prompt_token_count 
                    output_tokens = response.usage_metadata.candidates_token_count
                    out_obj = {"input_tokens":input_tokens,"output_tokens":output_tokens,"text":""}
                    returnData = response.text
                      
                except Exception as e:
                    print(f"Error saving file: {e}")
    with open(output_filename, "w", encoding="utf-8") as file:
                       file.write(returnData)    
    print("Image Extracted")
    write_summary(returnData)    

    return returnData
     
    
    

@user_agent.register_for_execution()
@video2text_conversion_agent.register_for_llm(description="You should execute the function")
def video_to_text(message:str) -> str:
    for root, dirs, files in os.walk(message):
        # Calculate relative path from source to current directory
        relative_path = os.path.relpath(root, message)

        # Create corresponding directory structure in destination
        dest_path = os.path.join("ExtractedFiles", relative_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            if file.lower().endswith(".mp4"):
                video_filepath = os.path.join(root, file)
                filename_without_ext, _ = os.path.splitext(file)
                output_filename = os.path.join(dest_path, f"{filename_without_ext}.txt")

                try:
                    video_text = ""
                    video_file_path = video_filepath
                    clip = mp.VideoFileClip(video_file_path)
                    clip.audio.write_audiofile(r"static/temp/videoconverted.wav")
                    audio = AudioSegment.from_wav(r"static/temp/videoconverted.wav")
                    n = len(audio)
                    counter = 1
                    interval = 20 * 1000
                    overlap = 1.5 * 1000
                    start = 0
                    end = 0
                    flag = 0
                    # chunks = split_on_silence(audio,min_silence_len = 500, silence_thresh = -40) 
                    Path(r'static/temp/video_chunks').parent.mkdir(parents=True,exist_ok=True) 
                    # print(chunks)
                    for i in range(0, 2 * n, interval):
                        if i == 0:
                            start = 0
                            end = interval
                        else:
                            start = end - overlap
                            end = start + interval 
                    
                        if end >= n:
                            end = n
                            flag = 1
                    
                        audio_chunk = audio[start:end]
                    
                        # Filename / Path to store the sliced audio
                        filename = 'chunk'+str(counter)+'.wav'
                        file = "static/temp/video_chunks/"+filename 
                        audio_chunk.export(file,format="wav")
                        print("Processing chunk "+str(counter)+". Start = "
                                        +str(start)+" end = "+str(end))
                        counter = counter + 1
                        r = sr.Recognizer() 
                        try:
                            with sr.AudioFile(file) as source: 
                                audio_listened = r.listen(source) 
                                rec = r.recognize_google(audio_listened) 
                                video_text += rec + " "
                        except:
                            pass
                    
                       
                except Exception as e:
                    print(f"Error saving file: {e}")   
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(video_text)
    print("Video Extracted", message)
    write_summary(video_text)    

    return video_text

def summarytxt(message):
    # print()
    try:
        with open(message, 'r', encoding='utf-8') as file:
            file_content = file.read()
        print(file_content)
        return file_content
    except FileNotFoundError:
        return f"Error: File not found at {message}"
    except Exception as e:
        return f"An error occurred: {e}"

@user_agent.register_for_execution()
@audio2text_conversion_agent.register_for_llm(description="You should execute the function")
def audio_to_text(message:str) -> str:
    # print()
    for root, dirs, files in os.walk(message):
        # Calculate relative path from source to current directory
        relative_path = os.path.relpath(root, message)

        # Create corresponding directory structure in destination
        dest_path = os.path.join("ExtractedFiles", relative_path)
        os.makedirs(dest_path, exist_ok=True)

        for file in files:
            if file.lower().endswith(".mp3"):
                audio_filepath = os.path.join(root, file)
                filename_without_ext, _ = os.path.splitext(file)
                output_filename = os.path.join(dest_path, f"{filename_without_ext}.txt")

                try:
                    audio_text = ""
                    audio_file_path = audio_filepath
                    clip = mp.AudioFileClip(audio_file_path)
                    clip.write_audiofile(r"static/temp/audioconverted.wav")
                    audio = AudioSegment.from_wav(r"static/temp/audioconverted.wav")
                    n = len(audio)
                    counter = 1
                    interval = 20 * 1000
                    overlap = 1.5 * 1000
                    start = 0
                    end = 0
                    flag = 0
                    # chunks = split_on_silence(audio,min_silence_len = 500, silence_thresh = -40) 
                    Path(r'static/temp/audio_chunks').parent.mkdir(parents=True,exist_ok=True) 
                    # print(chunks)
                    for i in range(0, 2 * n, interval):
                        if i == 0:
                            start = 0
                            end = interval
                        else:
                            start = end - overlap
                            end = start + interval 
                    
                        if end >= n:
                            end = n
                            flag = 1
                    
                        audio_chunk = audio[start:end]
                    
                        # Filename / Path to store the sliced audio
                        filename = 'chunk'+str(counter)+'.wav'
                        file = "static/temp/audio_chunks/"+filename 
                        audio_chunk.export(file,format="wav")
                        print("Processing chunk "+str(counter)+". Start = "
                                        +str(start)+" end = "+str(end))
                        counter = counter + 1
                        r = sr.Recognizer() 
                        try:
                            with sr.AudioFile(file) as source: 
                                audio_listened = r.listen(source) 
                                rec = r.recognize_google(audio_listened) 
                                audio_text += rec + " "
                        except:
                            pass
    
                       
                except Exception as e:
                    print(f"Error saving file: {e}")   

    with open(output_filename, "w", encoding="utf-8") as file:
                       file.write(audio_text)                
    print("Audio Extracted")   
    write_summary(audio_text)    
 
    return audio_text


# Start a sequence of two-agent chats.
# Each element in the list is a dictionary that specifies the arguments
# for the initiate_chat method.
chat_results = user_agent.initiate_chats(
    [
        {
            "recipient": pdf2text_conversion_agent,
            "message": "../Data/PatientData/Amy Cripto",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": video2text_conversion_agent,
            "message": "../Data/PatientData/Amy Cripto",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
         {
            "recipient": audio2text_conversion_agent,
            "message": "../Data/PatientData/Amy Cripto",
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": image2text_conversion_agent,
            "message": "../Data/PatientData/Amy Cripto",
            "max_turns": 2,
            "summary_method": "last_msg",
        }
    ]
)


    
summarytxt("static/DataFiles/PatientSummary.txt")