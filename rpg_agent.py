from dotenv import load_dotenv
# Get tokens
load_dotenv()

from discord import Message

import discord_tools.chat as chat_
from rpg_tools import prompts, reasoner
from discord_tools import dd_client, send_message, DISCORD_BOT_TOKEN
from discord_tools.commands import COMMAND_CHARS
from llm_tools import model

def get_responses(model, chat: chat_.Chat, reasoner: reasoner.RpgReasoner):
    # Faça uma solicitação de geração de texto
    return reasoner.GenerateRequest(chat, model)
            
# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, reasoner: reasoner.RpgReasoner):
    if not message.content:
        print("Message none error")
    async with message.channel.typing():
        try:
            for response in get_responses(model, chat, reasoner):
                await send_message(message.channel, response)
        except Exception as e:
            print("Error in get response", e, e.__traceback__)

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
    if dd_client.user in message.mentions or message.content[0] in COMMAND_CHARS:
        await respond_message(my_chat, message, my_reasoner)


dd_client.run(token=DISCORD_BOT_TOKEN)
