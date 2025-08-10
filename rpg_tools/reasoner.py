import traceback
import os
from enum import Enum
from google.generativeai import types
import discord_tools.chat as chat_
import rpg_tools.prompts as prompts
from rpg_tools.agentic_tools.dice import JogarD20
from rpg_tools.agentic_tools.rpg_init import RpgInit
from rpg_tools.agentic_tools import ToolSettings
from rpg_tools.agentic_tools.world_history import WorldHistoryTool, WorldHistoryTool_explanation, WorldHistoryTool_glm

from llm_tools import LanguageModel
from discord_tools.commands import COMMAND_CHARS

class RpgState(Enum):
    Initializing = 1
    CharacterCreation = 2
    History = 3
    Conversation = 4
    WorldBuild = 5

class RpgReasoner:
    state: RpgState = RpgState.Conversation
    world_history: WorldHistoryTool
    tool_settings: ToolSettings
    rpg_init: RpgInit
    
    def __init__(self):
        self.world_history = WorldHistoryTool()
        self.tool_settings = ToolSettings()
        self.rpg_init = None
    
    def GenerateRequest(self, chat: chat_.Chat, model: LanguageModel) -> list[str]:
        to_return: list[str] = []
        try:
            if self.state is RpgState.Conversation:
                return self.ConversationRequest(chat, model)
            elif self.state is RpgState.Initializing:
                return self.InitializingRequest(chat, model)
            elif self.state is RpgState.WorldBuild:
                return self.WorldBuild(chat, model)
            else:
                to_return.append(f"WARNING: State {self.state} in construction")
                print(to_return)
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request. CodeGR1")
            
        return to_return
    
    def ConversationRequest(self, chat: chat_.Chat, model: LanguageModel):
        to_return: list[str] = []
        try:
            req = prompts.preinit + self.tool_settings.get_conversation_tools_explanation() + self.world_history.GetHistory() + prompts.chatBuild(chat.messages) + prompts.postinit()
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request. Code CR1")
            
        if len(to_return) == 0:
            try:
                response: types.GenerateContentResponse = model.generate_content_with_functions(req, self.tool_settings.get_tool_list())
            except Exception as e:    
                print("Error in generation")
                to_return.append("An internal error ocurred while generating answer. Code CR2")
                traceback.print_exc()
                return to_return
            for part in response.parts:
                if part.text:
                    if part.text[0] in COMMAND_CHARS:
                        # Não responder texto com códigos
                        to_return.append(part.text[1:])
                    else:
                        to_return.append(part.text)
                    
                if part.function_call:
                    match part.function_call.name:
                        case "JogarD20":
                            resultado_dado = JogarD20()
                            print(f"@JogarD20 with result {resultado_dado}")
                            # Dar uma mensagem de follow up com o resultado
                            to_return.insert(0, f"@ O resultado do dado D20 foi {resultado_dado}")
                        case "InicializarRPG":
                            to_return += self.InitializeRpg(chat, model)
                        case _:
                            to_return.insert(0, f"Function called but not implemented: {part.function_call.name}")
                            print(to_return)
        return to_return
    
    def InitializeRpg(self, chat: chat_.Chat, model: LanguageModel) -> list[str]:
        # OK: Mensagens e ferramentas para a inicialização
        # TODO: Formalizar protocolo de inicialização
        # TODO: Salvar os dados da sessão no longo prazo
        self.state = RpgState.Initializing
        self.rpg_init = RpgInit()
        return self.InitializingRequest(chat, model)
        
    
    def InitializingRequest(self, chat: chat_.Chat, model: LanguageModel):
        # Remove a ferramenta de inicializar rpg, para mitigar um bug de a chamar em loop
        self.tool_settings.remove_tool("InitRPG")
        
        self.state = RpgState.WorldBuild
        return ["Primeiramente, diga aqui como quer que seja o mundo de RPG. Será um mundo medieval, cyberpunk, de fantasia, \
ou uma odisseia cósmica? Escreva aqui todas as informações essenciais, que preencherei o restante."]
        
    def WorldBuild(self, chat: chat_.Chat, model: LanguageModel) -> list[str]:
        to_return: list[str] = []
        self.state = RpgState.Conversation
        try:
            req = prompts.preinit_create_history + WorldHistoryTool_explanation + prompts.chatBuild(chat.messages) + prompts.postinit_alt() + prompts.postinit_create_history
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request. CodeWB2")
            
        if len(to_return) == 0:
            try:
                response: types.GenerateContentResponse = model.generate_content_with_functions(req, functions=[WorldHistoryTool_glm])
            except Exception as e:    
                print("Error in generation")
                traceback.print_exc()
                to_return.append("An internal error ocurred while generating answer. CodeWB3")
                return to_return
            for part in response.parts:
                if part.text:
                    if part.text[0] in COMMAND_CHARS:
                        # Não responder texto com códigos
                        to_return.append(part.text[1:])
                    else:
                        to_return.append(part.text)
                    
                if part.function_call:
                    match part.function_call.name:
                        case "InicializarHistoria":
                            to_return.append(self.world_history.WriteHistory(**part.function_call.args))
                            to_return.append(f"@ A aventura foi inicializada")
                        case _:
                            to_return.insert(0, f"Function called but not implemented: {part.function_call.name}")
                            print(to_return)
        return to_return
    
class ReasonerManager:
    channel_reasoner: dict
    
    def __init__(self):
        self.channel_reasoner = dict()
    
    def add_channel(self, channel) -> RpgReasoner:
        if channel in self.channel_reasoner.keys():
            return self.channel_reasoner[channel]
        else:
            reasoner = self.channel_reasoner[channel] = RpgReasoner()
        return reasoner
    
GlobalReasonerManager = ReasonerManager()
    
    