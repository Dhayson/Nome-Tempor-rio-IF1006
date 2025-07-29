import google.generativeai as genai
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from google.generativeai import types

import chat as chat_
from rpg_tools import prompts, reasoner
from rpg_tools.agentic_tools import Tool_list



def get_response(model, chat: chat_.Chat, reasoner: reasoner.RpgReasoner):
    # Faça uma solicitação de geração de texto
    return reasoner.GenerateRequest(chat, model)



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
tools = types.Tool(function_declarations=Tool_list)
model = genai.GenerativeModel('gemini-2.5-flash-lite', tools=[tools])

# Setup bot
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, reasoner: reasoner.RpgReasoner):
    if not message.content:
        print("Message none error")
    async with message.channel.typing():
        try:
            for response in get_response(model, chat, reasoner):
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
    prompts.LLM_NAME = client.user.display_name

# Incoming message
@client.event
async def on_message(message: Message):
    username: str = str(message.author.display_name)
    
    if message.content == "":
        return
    
    channel = message.channel
    
    my_chat = await chat_.GlobalManager.add_channel(channel)
    my_reasoner = reasoner.GlobalReasonerManager.add_channel(channel)
    my_chat.SetName(client.user.display_name)
    
    my_chat.add_message(message, username)
    
    # @ significa dar uma mensagem de follow up, após um comando
    if client.user in message.mentions or message.content[0] == '@':
        await respond_message(my_chat, message, my_reasoner)
    
client.run(token=DISCORD_BOT_TOKEN)
