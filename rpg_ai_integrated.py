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
from rpg_tools.reasoner import GlobalReasonerManager
from rag import get_rag_system

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de tokens
GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN2")

if not GOOGLE_API_TOKEN:
    raise ValueError("GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORD_TOKEN2 não encontrada nas variáveis de ambiente")

# Configurar Gemini
genai.configure(api_key=GOOGLE_API_TOKEN)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Configurar bot Discord
intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)

# Sistema RAG global
rag_system = None

async def initialize_systems():
    """Inicializa todos os sistemas necessários"""
    global rag_system
    
    print("🚀 Inicializando RPG.AI-Gemini...")
    
    # Inicializar sistema RAG
    print("📚 Inicializando sistema RAG D&D...")
    rag_system = get_rag_system()
    if rag_system:
        print("✅ Sistema RAG inicializado")
    else:
        print("⚠️ Sistema RAG não disponível")
    
    print("✅ Todos os sistemas inicializados!")

async def respond_with_rag(chat: chat_.Chat, message: Message, username: str) -> str:
    """Responde usando o sistema RAG para perguntas sobre D&D"""
    if not rag_system:
        return "❌ Sistema RAG não disponível"
    
    try:
        response = rag_system.generate_answer(chat, message.content)
        return response
    except Exception as e:
        print(f"Erro no RAG: {e}")
        return f"❌ Erro ao consultar regras D&D: {str(e)}"

async def respond_with_rpg(chat: chat_.Chat, message: Message, username: str, reasoner) -> list[str]:
    """Responde usando o agente RPG"""
    try:
        # Usar o reasoner para gerar resposta
        responses = reasoner.GenerateRequest(chat, model)
        return responses
    except Exception as e:
        print(f"Erro no agente RPG: {e}")
        return [f"❌ Erro no agente RPG: {str(e)}"]

def should_use_rag(message_content: str) -> bool:
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

async def send_response(channel: TextChannel, response: str):
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

@client.event
async def on_message(message: Message):
    """Processa mensagens recebidas"""
    # Ignorar mensagens do próprio bot
    if message.author == client.user:
        return
    
    # Ignorar mensagens vazias
    if not message.content or message.content.strip() == "":
        return
    
    username = str(message.author.display_name)
    channel = message.channel
    
    print(f"📨 Mensagem de {username} em #{channel.name}: {message.content}")
    
    # Adicionar ao chat
    my_chat = await chat_.GlobalManager.add_channel(channel)
    my_chat.SetName(client.user.display_name)
    my_chat.add_message(message, username)
    
    # Adicionar ao reasoner RPG
    my_reasoner = GlobalReasonerManager.add_channel(channel)
    
    # Verificar se o bot foi mencionado
    if client.user in message.mentions:
        async with channel.typing():
            try:
                # Determinar se deve usar RAG ou RPG
                if should_use_rag(message.content):
                    print("🔍 Usando sistema RAG para consulta D&D")
                    response = await respond_with_rag(my_chat, message, username)
                    await send_response(channel, response)
                else:
                    print("🎲 Usando agente RPG para resposta")
                    responses = await respond_with_rpg(my_chat, message, username, my_reasoner)
                    for response in responses:
                        await send_response(channel, response)
                        
            except Exception as e:
                error_msg = f"❌ Erro ao processar mensagem: {str(e)}"
                print(error_msg)
                await channel.send(error_msg)

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
