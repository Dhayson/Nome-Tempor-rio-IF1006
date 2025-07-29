import google.generativeai as genai
from google.generativeai import types
import os
from dotenv import load_dotenv
from rpg_tools.agentic_tools.dice import JogarD20, D20_tool

tools = types.Tool(function_declarations=[D20_tool])


load_dotenv()

# Pegar a chave de api
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Escolha o modelo
model = genai.GenerativeModel('gemini-2.0-flash-lite', tools=[tools])

chat = """Você ẽ um chat bot, que terã uma conversa com um usuãrio
Você tem acesso a um dado D20, que deve ser usado para gerar números
Agora iniciam as mensagens:
"""

new_message = True
D20once = True
while True:
    # Faça uma solicitação de geração de texto
    prompt = ""
    if new_message:
        D20once = True
        prompt = input("Prompt: ")
    if prompt != "":
        chat += "\nMensagem do usuário: " + prompt + "\nMensagem do modelo: "
    else:
        chat += "\nMensagem do modelo: "
    response = model.generate_content(chat)
    # Imprima a resposta
    for part in response.parts:
        new_message = True
        if part.text:
            print("\nResponse: ", part.text, "\n")
            chat += part.text
        if part.function_call:
            if D20once:
                result = JogarD20()
                D20once = False
                print(f"\nResultado do dado: {result}")
                chat += f"\nResultado do dado: {result}"
                new_message = False
    # print("\nOutput: ",response.parts)
