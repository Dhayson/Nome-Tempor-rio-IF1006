from discord import TextChannel, Message
import datetime
from discord_tools.conversion import parse_message
from discord_tools.commands import COMMAND_CHARS
  
    
class ChatMessage:
    discord_message: Message
    time: datetime.datetime
    username: str
    
    def __init__(self, msg: Message, time: datetime.datetime, username: str):
        self.discord_message = msg
        self.time = time
        self.username = username

class Chat:
    preinitialization = """
    Você é um modelo de linguagem conversando num chat de Discord\n
    As mensagens anteriores são sinalizadas com "$ Mensagem de x:" e "$ Mensagem do modelo:"\n
    Não escreva essas sinalizações, apenas construa a próxima mensagem\n
    Cite outros usuários utilizando @[nome-do-usuário]\n
    Responda continuando a conversa de forma natural, continuando e contribuindo para o tópico em questão\n
    Agora iniciam as mensagens:\n
    """
    chat_text = ""
    messages: list[ChatMessage] = []

    postinitialization = ""
    def __init__(self, nome = None):
        self.SetName(nome)
        self.messages = []
        self.chat_text = ""
    
    def SetName(self, nome = None, timestamp = True):
        if nome is not None:
            self.postinitialization = lambda:  f"\n\n$ Mensagem de {nome}:"
        elif timestamp:
            self.postinitialization = lambda: f"\n\n$ Mensagem de {nome} às {datetime.datetime.now()}:"
        else:
            self.postinitialization = lambda: "\n\n$ Mensagem do modelo: "
            
    def add_message(self, message: Message, username: str):
        message_content = message.content
        # Não acrescentar mensagens de comandos
        if message_content[0] in  ['!', '\\']:
            return
        elif message_content[0] in ['&']:
            message_content = message_content[1:]
        self.messages.append(ChatMessage(message, message.created_at, username))
        new_message = f"$ Mensagem de {username} às {message.created_at}: " + parse_message(message) + "\n\n\n"
        # print(f"{message.channel}|{username}|{message.author.id}:\n", new_message)
        self.chat_text += new_message
    
    async def RecoverHistory(self, channel: TextChannel):
        print(f"Recovering history from channel {channel.name}")
        hist = channel.history(oldest_first=True)
        hist = [mes async for mes in hist]
        for message in hist[:-1]:
            self.add_message(message, str(message.author.display_name))


class ChatManager:
    channel_chat: dict
    
    def __init__(self):
        self.channel_chat = dict()
    
    async def add_channel(self, channel):
        if channel.name in self.channel_chat.keys():
            return self.channel_chat[channel.name]
        else:
            self.channel_chat[channel.name] = Chat()
            chat = self.channel_chat[channel.name]
            await chat.RecoverHistory(channel)
            print(f"Current chats: {self.channel_chat}")
            return chat

GlobalManager = ChatManager()