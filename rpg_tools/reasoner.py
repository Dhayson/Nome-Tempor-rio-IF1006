from enum import Enum
from google.generativeai import types
import discord_tools.chat as chat_
from rpg_tools.agentic_tools.world_history import WorldHistoryTool
import rpg_tools.prompts as prompts
from rpg_tools.agentic_tools.dice import JogarD20
from rpg_tools.agentic_tools.rpg_init import RpgInit
from rpg_tools.agentic_tools import All_tools_explanation
from llm_tools import LanguageModel
from discord_tools.commands import COMMAND_CHARS

class RpgState(Enum):
    Initializing = 1
    CharacterCreation = 2
    History = 3
    Conversation = 4

class RpgReasoner:
    state: RpgState = RpgState.Conversation
    world_history: WorldHistoryTool
    rpg_init: RpgInit
    
    def __init__(self):
        self.world_history = WorldHistoryTool()
        self.rpg_init = None
    
    def GenerateRequest(self, chat: chat_.Chat, model: LanguageModel) -> list[str]:
        to_return: list[str] = []
        try:
            if self.state is RpgState.Conversation:
                return self.ConversationRequest(chat, model)
            elif self.state is RpgState.Initializing:
                return self.InitializingRequest(chat, model)
            else:
                to_return.append(f"WARNING: State {self.state} in construction")
                print(to_return)
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request")
            
        return to_return
    
    def ConversationRequest(self, chat: chat_.Chat, model: LanguageModel):
        to_return: list[str] = []
        try:
            req = prompts.preinit + All_tools_explanation + self.world_history.GetHistory() + prompts.chatBuild(chat.messages) + prompts.postinit()
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request")
            
        if len(to_return) == 0:
            try:
                response: types.GenerateContentResponse = model.generate_content(req)
            except Exception as e:    
                print("Error in generation", e, e.__traceback__)
                to_return.append("An internal error ocurred while generating answer")
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
                            to_return.insert(0, self.InitializeRpg(chat, model))
                        case _:
                            to_return.insert(0, f"Function called but not implemented: {part.function_call.name}")
                            print(to_return)
        return to_return
    
    def InitializeRpg(self, chat: chat_.Chat, model: LanguageModel):
        # TODO: Mensagens e ferramentas para a inicialização
        # TODO: Formalizar protocolo de inicialização
        # TODO: Salvar os dados da sessão no longo prazo
        self.state = RpgState.Initializing
        self.rpg_init = RpgInit()
        return self.InitializingRequest(chat, model)
        
    
    def InitializingRequest(self, chat: chat_.Chat, model: LanguageModel):
        self.state = RpgState.Conversation
        return ["RPG Initialization failed or incomplete"]
    
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
    
    