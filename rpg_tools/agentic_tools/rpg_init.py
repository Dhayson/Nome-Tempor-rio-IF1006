import random

from llm_tools import LanguageModel
import discord_tools.chat as chat_

Init_RPG_tool = {
    "name": "InicializarRPG",
    # OBSERVAÇÃO: a escolha da decrição impacta significativamente no comportamento do modelo
    "description": "Inicializa uma partida de rpg",
    "parameters":{
        "type": "object",
        },
}


Init_RPG_tool_explanation = """Sempre que um usuário solicitar, você tem uma ferramenta para inicializar uma seção de RPG
Ela deve obrigatoriamente ser chamada, para assim serem realizados os procedimentos necessãrios
"""

class RpgInit:
    def __init__(self):
        pass
    
    
    
    
    