# TODO: corrigir problema que essa função fica sendo chamada em loop, mesmo após ter sido executada
# Provavelmente é melhor a desabilitar durante a aventura

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
    
    
    
    
    