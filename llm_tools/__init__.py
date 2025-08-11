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
    
    @abstractmethod
    def configure(self, model_name: str, functions: list):
        pass
    
class GeminiModel(LanguageModel):
    tools: types.Tool
    model: genai.GenerativeModel
    
    def __init__(self, model_name: str, functions: list):
        super().__init__()
        if functions and len(functions) > 0:
            self.tools = types.Tool(function_declarations=functions)
            self.model = genai.GenerativeModel(model_name, tools=[self.tools])
        else:
            self.tools = None
            self.model = genai.GenerativeModel(model_name)
        
    def generate_content(self, req) -> types.GenerateContentResponse:
        print("DOING REQUEST")
        print(req)
        print("REQUEST DONE")
        return self.model.generate_content(req)
    
    def generate_content_with_functions(self, req, functions) -> types.GenerateContentResponse:
        print("DOING REQUEST WITH FUNCTIONS")
        print(req)
        print("REQUEST DONE")
        print(functions)
        print("FUNCTIONS DONE")
        if isinstance(functions, list):
            if functions and len(functions) > 0:
                functions = types.Tool(function_declarations=functions)
            else:
                # Se não há ferramentas, usar generate_content normal
                return self.model.generate_content(req)
        return self.model.generate_content(req, tools=[functions])
    
    def configure(self, model_name: str, functions: list):
        # Recriar o modelo com as novas configurações usando a mesma lógica do __init__
        if functions and len(functions) > 0:
            self.tools = types.Tool(function_declarations=functions)
            self.model = genai.GenerativeModel(model_name, tools=[self.tools])
        else:
            self.tools = None
            self.model = genai.GenerativeModel(model_name)
    
