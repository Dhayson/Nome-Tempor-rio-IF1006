import random

def JogarD20():
    return random.randint(1,20)

D20_tool = {
    "name": "JogarD20",
    # OBSERVAÇÃO: a escolha da decrição impacta significativamente no comportamento do modelo
    "description": "Role um D20, gerando um número uniformemente aleatório entre 1 e 20. Chame quando for escolher um número aleatório.",
    "parameters":{
        "type": "object",
        },
}