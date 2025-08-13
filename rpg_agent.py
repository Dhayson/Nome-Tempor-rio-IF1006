import os
from dotenv import load_dotenv
import google.generativeai as genai

from llm_tools import GeminiModel
# Get tokens
load_dotenv()

from discord import Message

import discord_tools.chat as chat_
from rpg_tools import reasoner
from discord_tools import dd_client, send_message, DISCORD_BOT_TOKEN
from discord_tools.commands import COMMAND_CHARS

def get_responses(model, chat: chat_.Chat, reasoner: reasoner.RpgReasoner):
    # Faça uma solicitação de geração de texto
    return reasoner.GenerateRequest(chat, model)

def expand_hist(model, chat: chat_.Chat, reasoner: reasoner.RpgReasoner):
    return reasoner.ExpandHistRequest(chat, model)
            
# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, reasoner: reasoner.RpgReasoner, func = get_responses):
    if not message.content:
        print("Message none error")
    async with message.channel.typing():
        try:
            for response in func(model, chat, reasoner):
                await send_message(message.channel, response)
        except Exception as e:
            print("Error in get response", e, e.__traceback__)


async def respond_command(chat: chat_.Chat, message: Message, reasoner: reasoner.RpgReasoner, char):
    if char == '&':
        await respond_message(chat, message, reasoner)
    elif chat == '\\':
        pass
    elif char == '!':
        if message.content[0:5] == "!help" or message.content[0:6] == "!ajuda":
            await send_message(message.channel,"""\\ Esses são os comandos disponíveis:
!expandir história: expande a história do mundo com os últimos acontecimentos
!help ou !ajuda: envia esta mensagem

Inicialize uma mensagem com \\ para ela não ser registrada pelo agente de rpg. Por exemplo, esta mensagem.
""")
        elif message.content[0:18] == "!expandir história":
            await respond_message(chat, message, reasoner, expand_hist)
        else:
            await send_message(message.channel, "Comandos ainda não implementados")

# Incoming message
@dd_client.event
async def on_message(message: Message):
    print("Got message")
    username: str = str(message.author.display_name)
    
    if message.content == "":
        return
    
    channel = message.channel
    
    my_chat = await chat_.GlobalManager.add_channel(channel)
    my_reasoner = reasoner.GlobalReasonerManager.add_channel(channel)
    my_chat.SetName(dd_client.user.display_name)
    
    my_chat.add_message(message, username)
    
    # @ significa dar uma mensagem de follow up, após um comando
    if message.content[0] in COMMAND_CHARS:
        await respond_command(my_chat, message, my_reasoner, message.content[0])
    elif dd_client.user in message.mentions:
        await respond_message(my_chat, message, my_reasoner)



GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_KEY")
# Setup llm
genai.configure(api_key=GOOGLE_API_TOKEN)
model = GeminiModel(os.getenv("MODEL"), [])
dd_client.run(token=DISCORD_BOT_TOKEN)
