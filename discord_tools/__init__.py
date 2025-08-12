from dotenv import load_dotenv
# Get tokens
load_dotenv()
from discord import Intents, Client, Message, TextChannel
import os
from rpg_tools import prompts

# Tokens
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# Setup bot
intents = Intents.default()
intents.message_content = True
dd_client = Client(intents=intents)



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

# Startup bot
@dd_client.event
async def on_ready():
    print(f"Client {dd_client.user} running!")
    prompts.LLM_NAME = dd_client.user.display_name
    

async def send_message(channel: TextChannel, response: str):
    if response is None or response == "":
        print("Empty response")
    
    try:
        if len(response) < 2000:
            await channel.send(response)
        else:
            for res in split_text_n(response, '\n', 1800):
                    if res != "":
                        await channel.send(res)
    except Exception as e:
        print("Error in sending message: ", e, e.__traceback__)
        
