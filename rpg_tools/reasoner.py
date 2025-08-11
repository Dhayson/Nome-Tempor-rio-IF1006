import traceback
import os
from enum import Enum
from google.generativeai import types
import discord_tools.chat as chat_
import rpg_tools.prompts as prompts
from rpg_tools.agentic_tools.dice import JogarD20
from rpg_tools.agentic_tools.rpg_init import RpgInit
from rpg_tools.agentic_tools import ToolSettings
from rpg_tools.agentic_tools.world_history import *
import google.ai.generativelanguage as glm

from llm_tools import LanguageModel
from discord_tools.commands import COMMAND_CHARS

# Importar sistema RAG
try:
    from rag import get_rag_system
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ Sistema RAG não disponível")

# Importar sistema de contexto Redis
try:
    from rpg_tools.context_manager import context_manager
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    print("⚠️ Sistema de contexto Redis não disponível")

class RpgState(Enum):
    Initializing = 1
    CharacterCreation = 2
    History = 3
    Conversation = 4
    WorldBuild = 5

class RpgReasoner:
    state: RpgState
    world_history: WorldHistoryTool
    tool_settings: ToolSettings
    rpg_init: RpgInit
    rag_system: any  # Sistema RAG para consultas D&D
    channel_id: str  # ID do canal Discord
    
    def __init__(self, channel_id: str = None):
        self.world_history = WorldHistoryTool()
        self.tool_settings = ToolSettings()
        self.state = RpgState.Conversation
        self.rpg_init = None
        self.channel_id = channel_id
        
        # Inicializar sistema RAG se disponível
        if RAG_AVAILABLE:
            try:
                self.rag_system = get_rag_system()
                if self.rag_system:
                    print("✅ Sistema RAG integrado ao agente RPG")
                else:
                    print("⚠️ Sistema RAG falhou ao inicializar")
                    self.rag_system = None
            except Exception as e:
                print(f"⚠️ Erro ao inicializar RAG: {e}")
                self.rag_system = None
        else:
            self.rag_system = None
    
    def _should_use_rag(self, query: str) -> bool:
        """Determina se deve usar RAG ou ferramentas RPG"""
        if not self.rag_system:
            return False
        
        # Se é uma pergunta sobre D&D, usar RAG
        if self.rag_system.is_dnd_question(query):
            return True
        
        # Se é uma pergunta sobre regras, usar RAG
        dnd_keywords = ['regra', 'regras', 'd&d', 'dnd', 'dungeons', 'dragons', 'classe', 'raça', 'magia', 'combate']
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in dnd_keywords):
            return True
        
        return False
    
    def _get_context_summary(self) -> str:
        """Obtém resumo do contexto Redis para usar nos prompts"""
        if not CONTEXT_AVAILABLE or not self.channel_id:
            return ""
        
        try:
            return context_manager.get_context_summary(self.channel_id)
        except Exception as e:
            print(f"Erro ao obter contexto: {e}")
            return ""
    
    def _update_context(self, message: str, username: str):
        """Atualiza o contexto Redis com uma nova mensagem"""
        if not CONTEXT_AVAILABLE or not self.channel_id:
            return
        
        try:
            context_manager.update_context(self.channel_id, message, username)
        except Exception as e:
            print(f"Erro ao atualizar contexto: {e}")
    
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
            # Verificar se deve usar RAG para a última mensagem
            last_message = ""
            if chat.messages:
                last_message = chat.messages[-1].discord_message.content
            
            # Atualizar contexto Redis com a mensagem
            if chat.messages:
                username = chat.messages[-1].username
                self._update_context(last_message, username)
            
            # Se deve usar RAG, gerar resposta RAG
            if self._should_use_rag(last_message):
                print("🔍 Usando sistema RAG para consulta D&D")
                try:
                    rag_response = self.rag_system.generate_answer(chat, last_message)
                    to_return.append(rag_response)
                    return to_return
                except Exception as e:
                    print(f"⚠️ Erro no RAG, usando ferramentas RPG: {e}")
                    # Fallback para ferramentas RPG
            
            # Obter contexto Redis para enriquecer o prompt
            context_summary = self._get_context_summary()
            
            # Usar ferramentas RPG normais com contexto enriquecido
            req = prompts.preinit + \
                self.tool_settings.get_conversation_tools_explanation() + \
                self.world_history.GetHistory() + \
                (f"\n📋 **CONTEXTO DA SESSÃO:**\n{context_summary}\n" if context_summary else "") + \
                prompts.chatBuild(chat.messages) + \
                prompts.postinit()
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
                        case "ExpandirHistoria":
                            to_return.append("História atualizada")
                            to_return.append(self.world_history.AddHistory(**part.function_call.args))
                        case _:
                            to_return.insert(0, f"Function called but not implemented: {part.function_call.name}")
                            print(to_return)
        return to_return
    
    def ExpandHistRequest(self, chat: chat_.Chat, model: LanguageModel) -> list[str]:
        to_return: list[str] = []
        try:
            # Obter contexto Redis para enriquecer o prompt
            context_summary = self._get_context_summary()
            
            req = prompts.preinit + \
                self.world_history.GetHistory() + \
                (f"\n📋 **CONTEXTO DA SESSÃO:**\n{context_summary}\n" if context_summary else "") + \
                prompts.chatBuild(chat.messages) + \
                prompts.postinit_alt() + \
                AddHistoryTool_explanation_alt
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating request. Code CR1")
            
        if len(to_return) == 0:
            try:
                response: types.GenerateContentResponse = model.generate_content_with_functions(req, [AddHistoryTool_glm])
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
                        case "ExpandirHistoria":
                            to_return.append("História atualizada")
                            to_return.append(self.world_history.AddHistory(**part.function_call.args))
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
            # Obter contexto Redis para enriquecer o prompt
            context_summary = self._get_context_summary()
            
            req = prompts.preinit_create_history + WorldHistoryTool_explanation + \
                  (f"\n📋 **CONTEXTO DA SESSÃO:**\n{context_summary}\n" if context_summary else "") + \
                  prompts.chatBuild(chat.messages) + prompts.postinit_alt() + prompts.postinit_create_history
        except Exception as e:
            print("Error in request formation", e, e.__traceback__)
            to_return.append("An internal error ocurred while generating answer. CodeWB2")
            
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
                            # self.tool_settings.add_tool("AddHist", AddHistoryTool_glm, AddHistoryTool_explanation)
                        case _:
                            to_return.insert(0, f"Function called but not implemented: {part.function_call.name}")
                            print(to_return)
        return to_return
    
class ReasonerManager:
    channel_reasoner: dict
    
    def __init__(self):
        self.channel_reasoner = dict()
    
    def add_channel(self, channel) -> RpgReasoner:
        if channel.name in self.channel_reasoner.keys():
            return self.channel_reasoner[channel.name]
        else:
            # Criar reasoner com ID do canal para contexto Redis
            reasoner = RpgReasoner(str(channel.id))
            self.channel_reasoner[channel.name] = reasoner
            print(f"Current reasoners: {self.channel_reasoner}")
            return reasoner
    
GlobalReasonerManager = ReasonerManager()
    
    