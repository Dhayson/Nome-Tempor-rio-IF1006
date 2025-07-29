from enum import Enum
from google.generativeai import types
import chat as chat_
from rpg_tools.world_history import WorldHistoryTool
import rpg_tools.prompts as prompts
from rpg_tools.agentic_tools.dice import JogarD20
from rpg_tools.agentic_tools import All_tools_explanation

class RpgState(Enum):
    Initializing = 1
    CharacterCreation = 2
    History = 3
    Conversation = 4

class RpgReasoner:
    state: RpgState = RpgState.Conversation
    world_history: WorldHistoryTool
    
    def __init__(self):
        self.world_history = WorldHistoryTool()
    
    def GenerateRequest(self, chat: chat_.Chat, model) -> list[str]:
        to_return: list[str] = []
        try:
            if self.state is RpgState.Conversation:
                req = prompts.preinit + All_tools_explanation + self.world_history.GetHistory() + prompts.chatBuild(chat.messages) + prompts.postinit()
            else:
                to_return.append(f"WARNING: State {self.state} in construction")
                print(to_return)
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
                    if part.text[0] in ['@']:
                        # Não responder texto com códigos
                        to_return.insert(0, part.text[1:])
                    else:
                        to_return.insert(0, part.text)
                    
                if part.function_call:
                    match part.function_call.name:
                        case "JogarD20":
                            resultado_dado = JogarD20()
                            print(f"@JogarD20 with result {resultado_dado}")
                            # Dar uma mensagem de follow up com o resultado
                            to_return.append(f"@ O resultado do dado D20 foi {resultado_dado}")
                        case _:
                            to_return = f"Function called but not implemented: {part.function_call.name}"
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
    
    