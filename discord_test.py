import google.generativeai as genai
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
import chat as chat_


def get_response(model, chat: chat_.Chat, message: Message, username):
    # Faça uma solicitação de geração de texto
    req = chat.preinitialization + chat.chat_text + chat.postinitialization()
    response = model.generate_content(req)
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
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN2")

# Setup llm
genai.configure(api_key=GOOGLE_API_TOKEN)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Setup bot
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)



# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, username: str):
    if not message.content:
        print("Message none error")
    async with message.channel.typing():
        try:
            response = get_response(model, chat, message, username)
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
            print("Error in get response", e, e.__traceback__)
        
# Startup bot
@client.event
async def on_ready():
    print(f"Client {client.user} running!")

# Incoming message
@client.event
async def on_message(message: Message):
    
    username: str = str(message.author.display_name)
    user_message: str = message.content
    channel = message.channel
    
    my_chat = await chat_.GlobalManager.add_channel(channel)
    my_chat.SetName(client.user.display_name)
    
    my_chat.add_message(message, username)
    
    if client.user in message.mentions:
        await respond_message(my_chat, message, username)
    
client.run(token=DISCORD_BOT_TOKEN)
