import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Pegar a chave de api
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Escolha o modelo
model = genai.GenerativeModel('gemini-2.0-flash-lite')

chat = """Você ẽ um chat bot, que terã uma conversa com um usuãrio
Agora iniciam as mensagens:
"""

while True:
    # Faça uma solicitação de geração de texto
    prompt = input("Prompt: ")
    if prompt != "":
        chat += "\nMensagem do usuário: " + prompt + "\nMensagem do modelo: "
    response = model.generate_content(chat)
    # Imprima a resposta
    print("\nResponse: ", response.text, "\n")
    
    chat += response.text