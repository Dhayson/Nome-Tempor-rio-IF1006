from enum import Enum
from abc import ABC, abstractmethod

import google.generativeai as genai
from google.generativeai import types
    
class LanguageModel(ABC):
    @abstractmethod
    def generate_content(self, req: str):
        pass
    
    @abstractmethod
    def generate_content_with_functions(self, req: str, tools):
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
    
    def generate_content_with_functions(self, req, functions) -> types.GenerateContentResponse:
        if functions is list:
            functions = types.Tool(function_declarations=functions)
        return self.model.generate_content(req, tools=functions)
    
