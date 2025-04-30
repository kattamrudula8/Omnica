
#  init_kernel code
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from dotenv import load_dotenv
import os
from gemini_functions import ContentAnalyzerPlugin

def init_kernel_with_analyze_content_with_gemini() -> Kernel:
    kernel = Kernel()

    # ✅ Instantiate the plugin class (not a function call)
    content_plugin = ContentAnalyzerPlugin()
    kernel.add_plugin(plugin=content_plugin, plugin_name="ContentAnalyzer")

    return kernel



# MAIN.py code

import asyncio
from semantic_kernel import Kernel
from init_kernel import init_kernel_with_analyze_content_with_gemini



@app.route("/fetch_topic")
def fetch_topic():
    print("fetch_topic")

    try:
        dbParams = json.loads(request.args.get("dbParams"))
        print(dbParams)
        userName = dbParams.get("userName")
        folderName = dbParams.get("selectedPatient", "").strip()
        file_name = dbParams.get("selectedFileName")

        if not all([userName, folderName, file_name]):
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400

        # Build file path
        data_folder = "TicketData"
        workspace_dir_path = workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folderName)
        full_file_path = os.path.join(dir_path, file_name)

        if not os.path.exists(full_file_path):
            return jsonify({
                "status": "error",
                "message": f"File not found at {full_file_path}"
            }), 404

        # Prompt for the agent
        prompt = (
            "Extract the main topics in the given file as a list. "
            "Gives only Topic header no summary and description of topic needed. "
            "Its important for you to remember to not provide any extra information, just provide headers in a valid list."
        )

        # ⚡ Step 1: Initialize kernel
        kernel = init_kernel_with_analyze_content_with_gemini()

        # ⚡ Step 2: Prepare arguments
        args = KernelArguments({
            "file_path": full_file_path,
            "prompt_text": prompt
        })

        # ⚡ Step 3: Call the SK plugin function
        try:
            plugin_result = asyncio.run(kernel.invoke("ContentAnalyzer", "call_gemini_file_analyzer", args))
            print("Plugin result raw output:", plugin_result)
            topics = str(plugin_result)
        except Exception as sk_err:
            print("SK agent error:", sk_err)
            return jsonify({"status": "error", "message": "Agent call failed"}), 500

        if topics:
            import ast
            try:
                parsed_topics = ast.literal_eval(topics)
                if not isinstance(parsed_topics, list):
                    parsed_topics = [t.strip("1234567890. ").strip() for t in topics.split("\n") if t.strip()]
            except:
                parsed_topics = [t.strip("1234567890. ").strip() for t in topics.split("\n") if t.strip()]

            return jsonify({"status": "success", "topics": parsed_topics})
        else:
            return jsonify({"status": "error", "message": "No topics found or agent failed"}), 500

    except Exception as exec:
        return jsonify({"status": "error", "message": str(exec)}), 500

# Plugin code - gemini_functions.py
import asyncio
from semantic_kernel.functions import KernelArguments
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
import os
from typing import Union, List

import google.generativeai as genai

import os
import base64



# HELPER FUNCTION
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class ContentAnalyzerPlugin:
    @kernel_function(name="summary_topics_agent", description="Call the gemini function to analyze given input file")
    def summary_topics_agent(self, file_path: str, prompt_text: str) -> str:

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()

            mime_type = self._get_mime_type(file_path)

            contents = [
                {
                    "parts": [
                        {"inline_data": {"mime_type": mime_type, "data": file_data}},
                        {"text": prompt_text}
                    ]
                }
            ]

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(contents)

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return f"ERROR: Blocked: {response.prompt_feedback.block_reason}"

            return response.text or "[]"
        
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def _get_mime_type(file_path: str) -> str:
        """
        Determines the MIME type of a file based on its extension.

        Args:
            file_path: The path to the file.

        Returns:
            The MIME type as a string, or "application/octet-stream" if unknown.
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        mime_types = {
            ".txt": "text/txt",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".mp4": "video/mp4",
            ".mpeg": "video/mpeg",
            ".mp3": "audio/mp3",
            ".wav": "audio/wav",
        }
        return mime_types.get(file_extension, "application/octet-stream")  # Default MIME type


# Other gemini function semnatic code
from semantic_kernel.skill_definition import kernel_function, sk_function
import os, json, ast

class FileGeminiHelper:

    def __init__(self, workspace_org_path, analyze_function):
        self.workspace_org_path = workspace_org_path
        self.analyze = analyze_function

    def _get_full_path(self, userName, folderName, fileName):
        data_folder = "TicketData"
        workspace_dir_path = self.workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folderName)
        full_file_path = os.path.join(dir_path, fileName)
        return full_file_path

    @kernel_function(name="detect_topics_agent")
    def detect_topics_agent(self, input_json: str) -> str:
        data = json.loads(input_json)
        userName = data["userName"]
        folder = data["selectedPatient"]
        file_name = data["selectedFileName"]
        topics = data["selectedTopics"]

        file_path = self._get_full_path(userName, folder, file_name)

        prompt = (
            f"Give Topics for the following selected file:\n"
            f"Do not include any unrelated content. Keep the Tpoics in list clear and concise."
        )

        return self.analyze(file_path, prompt)

    @kernel_function(name="file_query_agent")
    def file_query_agent(self, input_json: str) -> str:
        data = json.loads(input_json)
        userName = data["userName"]
        folder = data["selectedPatient"]
        file_name = data["selectedFileName"]
        query = data["userQuery"]

        file_path = self._get_full_path(userName, folder, file_name)

        prompt = f"Based on the contents of the uploaded file, answer this question:\n\n{query}\n\nYour response should be clear and context-aware."

        return self.analyze(file_path, prompt)

    @kernel_function(name="enumerate_files_agent")
    def enumerate_files_agent(self, input_json: str) -> str:
        data = json.loads(input_json)
        userName = data["userName"]
        folder = data["selectedPatient"]
        data_folder = "TicketData"

        workspace_dir_path = self.workspace_org_path.replace("<USERNAME>", userName) + "Data/" + data_folder + "/"
        dir_path = os.path.join(workspace_dir_path, folder)

        if not os.path.exists(dir_path):
            return json.dumps({"status": "error", "message": "Directory not found"})

        files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        return json.dumps({"status": "success", "files": files})

    @kernel_function(name="followup_actions_agent")
    def followup_actions_agent(self, input_json: str) -> str:
        data = json.loads(input_json)
        userName = data["userName"]
        folder = data["selectedPatient"]
        file_names = data["selectedPatientFile"]

        workspace_dir_path = self.workspace_org_path.replace("<USERNAME>", userName) + "Data/TicketData/"
        dir_path = os.path.join(workspace_dir_path, folder)

        prompt = (
            "You are analyzing a patient's record to create a list of recommended actions.\n"
            "Based on the content of the given file, return two structured lists:\n"
            "1. Action List for Doctor\n"
            "2. Action List for Patient\n\n"
            "Each list should include actionable points in bullet format.\n"
            "Do NOT include any additional explanation or introductory text.\n"
            "Return a valid JSON object with two keys: 'doctor' and 'patient'."
        )

        result = {}
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            if not os.path.isfile(file_path):
                result[file_name] = {"doctor": [], "patient": [], "error": "File not found"}
                continue
            try:
                actions = self.analyze(file_path, prompt)
                action_dict = ast.literal_eval(actions)
                result[file_name] = {
                    "doctor": action_dict.get("doctor", []),
                    "patient": action_dict.get("patient", [])
                }
            except Exception as e:
                result[file_name] = {"doctor": [], "patient": [], "error": str(e)}

        return json.dumps(result)
