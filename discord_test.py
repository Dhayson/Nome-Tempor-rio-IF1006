import google.generativeai as genai
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
import chat as chat_
from rag import get_rag_system


def get_response(model, chat: chat_.Chat, prompt, username):
    # Verificar se é pergunta sobre D&D e se RAG está disponível
    rag_system = get_rag_system()
    
    if rag_system and rag_system.is_dnd_question(prompt):
        print(f"🎲 Detectada pergunta D&D de {username}: {prompt}")
        try:
            # Usar RAG para responder perguntas sobre D&D
            response_text = rag_system.generate_answer(prompt)
            chat.chat_text += f"\n\n$ Mensagem de {username}: " + prompt + "\n"
            chat.chat_text += f"$ Mensagem de {client.user.display_name} (D&D RAG): " + response_text
            return response_text
        except Exception as e:
            print(f"❌ Erro no RAG: {e}")
            # Se RAG falhar, continuar com chat normal
    
    # Chat normal para outras perguntas
    chat.chat_text += f"\n\n$ Mensagem de {username}: " + prompt + "\n"
    print("\nCURRENT CHAT\n", chat.chat_text, "\n\nEND CURRENT CHAT\n")
    req = chat.preinitialization + chat.chat_text + chat.postinitialization
    response = model.generate_content(req)
    chat.chat_text += f"$ Mensagem de {client.user.display_name}: " + response.text
    return response.text



def split_text_n(text: str, sep, n):
    idx_res = -1
    idx_src = 0
    next_word = True
    final_texts_array = []
    text_split = text.split(sep)
    while True:
        if len(text_split) == idx_src:
            break
        if next_word:
            idx_res += 1
            final_texts_array.append(text_split[idx_src])
            next_word = False
        else:
            if len(text_split[idx_src]) + len(final_texts_array[idx_res]) < n:
                final_texts_array[idx_res] += text_split[idx_src] + '\n'
            else:
                next_word = True
                continue
        idx_src += 1
    return final_texts_array
            
        

# Get discord token
load_dotenv()

# Tokens
GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup llm
genai.configure(api_key=GOOGLE_API_TOKEN)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Setup bot
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)



# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, user_message: str, username: str):
    if not user_message:
        print("Message none error")
    
    try:
        response = get_response(model, chat, user_message, username)
        if len(response) < 2000:
            await message.channel.send(response)
        else:
            for res in split_text_n(response, '\n', 1800):
                try:
                    if res != "":
                        await message.channel.send(res)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
        
# Startup bot
@client.event
async def on_ready():
    print(f"Client {client.user} running!")
    
    # Inicializar sistema RAG D&D
    print("🎲 Carregando sistema RAG D&D...")
    rag_system = get_rag_system()
    if rag_system:
        print("✅ Sistema RAG D&D carregado com sucesso!")
    else:
        print("⚠️ Sistema RAG D&D não pôde ser carregado. Bot funcionará sem RAG.")

# Incoming message
@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    
    username: str = str(message.author.display_name)
    user_message: str = message.content
    channel = message.channel
    
    my_chat = await chat_.GlobalManager.add_channel(channel)
    my_chat.SetName(client.user.display_name)
    
    print(f"{channel}|{username}|{message.author.id}: {user_message}")
    if client.user in message.mentions:
        await respond_message(my_chat, message, user_message, username)
    else:
        await my_chat.add_message(message, username)
    
client.run(token=DISCORD_BOT_TOKEN)