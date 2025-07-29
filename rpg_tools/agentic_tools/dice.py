import random

def JogarD20():
    return random.randint(1,20)

D20_tool = {
    "name": "JogarD20",
    # OBSERVAÇÃO: a escolha da decrição impacta significativamente no comportamento do modelo
    "description": "Role um D20, gerando um número uniformemente aleatório entre 1 e 20. Chame quando for escolher um número aleatório após uma ação ou for rolar um D20.",
    "parameters":{
        "type": "object",
        },
}


D20_tool_explanation = """Você tem acesso a um dado D20, pela função JogarD20
Isso deve ser usado ao gerar um número aleatório, durante a seção de RPG com uma ação correspondente do usuário \
ou então quando for pedido explicitamente.
Não diga que rolou um D20 sem utilizar a ferramenta.
"""