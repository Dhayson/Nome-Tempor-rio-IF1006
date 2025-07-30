from enum import Enum
from abc import ABC, abstractmethod

import google.generativeai as genai
from google.generativeai import types
import os
from rpg_tools.agentic_tools import Tool_list

GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_KEY")
# Setup llm
genai.configure(api_key=GOOGLE_API_TOKEN)
    
class LanguageModel(ABC):
    @abstractmethod
    def generate_content(self, req: str):
        pass
    
class GeminiModel(LanguageModel):
    tools: types.Tool
    model: genai.GenerativeModel
    
    def __init__(self, model_name: str, functions: list):
        super().__init__()
        self.tools = types.Tool(function_declarations=functions)
        self.model = genai.GenerativeModel(model_name, tools=[self.tools])
        
    def generate_content(self, req) -> types.GenerateContentResponse:
        return self.model.generate_content(req)
    

model = GeminiModel('gemini-2.5-flash-lite', Tool_list)