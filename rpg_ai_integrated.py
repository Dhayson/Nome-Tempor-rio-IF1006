#!/usr/bin/env python3
"""
RPG.AI-Gemini - Bot Discord Integrado
Sistema unificado que combina agente RPG com sistema RAG D&D
"""

import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from discord import Intents, Client, Message, TextChannel
import discord_tools.chat as chat_
from rpg_tools.reasoner import GlobalReasonerManager, RpgReasoner
from rag import get_rag_system
from llm_tools import GeminiModel
from rpg_tools.agentic_tools import ToolSettings
from discord_tools.commands import COMMAND_CHARS

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de tokens
GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN2")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if not GOOGLE_API_TOKEN:
    raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_TOKEN não encontrada nas variáveis de ambiente")

# Configurar Gemini
genai.configure(api_key=GOOGLE_API_TOKEN)

# Inicializar ferramentas RPG para o modelo
tool_settings = ToolSettings()
model = GeminiModel('gemini-2.5-flash', tool_settings.get_tool_list())

# Configurar bot Discord
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)

# Sistema RAG global
rag_system = None

# Sistema de contexto Redis
context_manager = None

async def initialize_systems():
    """Inicializa todos os sistemas necessários"""
    global rag_system, context_manager
    
    print("🚀 Inicializando RPG.AI-Gemini...")
    
    # Inicializar sistema RAG
    print("📚 Inicializando sistema RAG D&D...")
    rag_system = get_rag_system()
    if rag_system:
        print("✅ Sistema RAG inicializado")
    else:
        print("⚠️ Sistema RAG não disponível")
    
    # Inicializar sistema de contexto Redis
    print("🗄️ Inicializando sistema de contexto Redis...")
    try:
        from rpg_tools.context_manager import context_manager as cm
        context_manager = cm
        print("✅ Sistema de contexto Redis inicializado")
    except Exception as e:
        print(f"⚠️ Sistema de contexto Redis não disponível: {e}")
        context_manager = None
    
    print("✅ Todos os sistemas inicializados!")

async def respond_with_rag(chat: chat_.Chat, message: Message) -> str:
    """Responde usando o sistema RAG para perguntas sobre D&D"""
    if not rag_system:
        return "❌ Sistema RAG não disponível"
    
    try:
        response = ["RESPOSTA: " + rag_system.generate_answer(chat, message.content)]
        return response
    except Exception as e:
        print(f"Erro no RAG: {e}")
        return f"❌ Erro ao consultar regras D&D: {str(e)}"

async def respond_with_rpg(chat: chat_.Chat, reasoner) -> list[str]:
    """Responde usando o agente RPG"""
    try:
        # Usar o reasoner para gerar resposta
        responses = reasoner.GenerateRequest(chat, model)
        return responses
    except Exception as e:
        print(f"Erro no agente RPG: {e}")
        return [f"❌ Erro no agente RPG: {str(e)}"]

def should_use_rag(message_content: str) -> bool:
    """Usar RAG para perguntas diretas"""
    if not message_content[-1] == '?':
        return False
    
    """Determina se deve usar RAG ou agente RPG"""
    if not rag_system:
        return False
    
    # Verificar se é pergunta sobre D&D
    if rag_system.is_dnd_question(message_content):
        return True
    
    # Verificar palavras-chave relacionadas a regras
    dnd_keywords = ['regra', 'regras', 'd&d', 'dnd', 'dungeons', 'dragons', 'classe', 'raça', 'magia', 'combate', 'ac', 'hp', 'dano']
    message_lower = message_content.lower()
    if any(keyword in message_lower for keyword in dnd_keywords):
        return True
    
    return False

async def send_message(channel: TextChannel, response: str):
    """Envia resposta para o canal Discord"""
    if not response or response.strip() == "":
        return
    
    # Dividir mensagens longas se necessário
    if len(response) > 1900:
        # Dividir por parágrafos
        parts = response.split('\n\n')
        current_part = ""
        
        for part in parts:
            if len(current_part) + len(part) + 2 > 1900:
                if current_part:
                    await channel.send(current_part.strip())
                current_part = part
            else:
                current_part += "\n\n" + part if current_part else part
        
        if current_part:
            await channel.send(current_part.strip())
    else:
        await channel.send(response)

@client.event
async def on_ready():
    """Evento executado quando o bot está pronto"""
    print(f"🤖 Bot {client.user} está online!")
    print(f"📱 Conectado em {len(client.guilds)} servidor(es)")
    
    # Inicializar sistemas
    await initialize_systems()

async def expand_hist(chat: chat_.Chat, reasoner: RpgReasoner):
    return reasoner.ExpandHistRequest(chat, model)

# Message functionality
async def respond_message(chat: chat_.Chat, message: Message, reasoner: RpgReasoner, func = respond_with_rpg):
    if not message.content:
        print("Message none error")
    async with message.channel.typing():
        try:
            for response in await func(chat, reasoner):
                await send_message(message.channel, response)
        except Exception as e:
            print("Error in get response", e, e.__traceback__)

async def respond_command(chat: chat_.Chat, message: Message, reasoner: RpgReasoner, char):
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

Mencione o bot e finalize a mensagem com ? para perguntar sobre RPG
""")
        elif message.content[0:18] == "!expandir história":
            await respond_message(chat, message, reasoner, expand_hist)
        else:
            await send_message(message.channel, "Comandos ainda não implementados")


@client.event
async def on_message(message: Message):
    """Processa mensagens recebidas"""
    
    # Ignorar mensagens vazias
    if not message.content or message.content.strip() == "":
        return
    
    username = str(message.author.display_name)
    channel = message.channel
    
    print(f"📨 Mensagem de {username} em #{channel.name}: {message.content}")
    
    # Adicionar ao chat
    my_chat: chat_.Chat = await chat_.GlobalManager.add_channel(channel)
    my_chat.SetName(client.user.display_name)
    my_chat.add_message(message, username)
    
    # Adicionar ao reasoner RPG (que agora gerencia contexto Redis)
    my_reasoner: RpgReasoner = GlobalReasonerManager.add_channel(channel)
    
    # Debug: mostrar informações sobre menções
    print(f"🔍 DEBUG: Bot ID: {client.user.id}")
    print(f"🔍 DEBUG: Menções na mensagem: {[str(mention.id) for mention in message.mentions]}")
    print(f"🔍 DEBUG: Bot mencionado? {client.user in message.mentions}")
    
    # Verificar se o bot foi mencionado (múltiplas formas)
    bot_mentioned = (
        message.content[0] == '&' or
        client.user in message.mentions or  # Menção direta
        f"<@{client.user.id}>" in message.content or  # Menção por ID
        f"<@!{client.user.id}>" in message.content  # Menção com nickname
    )
    
    if message.content[0] in COMMAND_CHARS:
        await respond_command(my_chat, message, my_reasoner, message.content[0])
    elif bot_mentioned:
        print("✅ Bot foi mencionado, processando...")
        try:
            # Determinar se deve usar RAG ou RPG
            if should_use_rag(message.content):
                print("🔍 Usando sistema RAG para consulta D&D")
                await respond_message(my_chat, message, message, respond_with_rag)
            else: 
                print("🎲 Usando agente RPG para resposta")
                await respond_message(my_chat, message, my_reasoner)
                    
        except Exception as e:
            error_msg = f"❌ Erro ao processar mensagem: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            await channel.send(error_msg)
    else:
        print("❌ Bot não foi mencionado, ignorando mensagem")

async def main():
    """Função principal"""
    try:
        print("🎮 Iniciando RPG.AI-Gemini...")
        await client.start(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executar o bot
    asyncio.run(main())
