
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


# LLM Configurations
config_list = [{'model': 'gemini-1.5-flash', 'api_key': GOOGLE_API_KEY, "api_type": "google"}]

llm_config = {
    "cache_seed": 42,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}