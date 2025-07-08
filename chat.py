from discord import TextChannel, Message
from user_id import GlobalUserId
import re

def convert_mention(mention: str):
    if not re.match("<@[0-9]+>$"):
        return mention
    id = int(mention[2:-1])
    return f"@{GlobalUserId.GetUser(id)}"
    

def parse_message(message: Message):
    content = message.content
    mention_flag = content[0] == '<'
    
    # Add users and their ids to the mapping, if at least one is missing
    all_users = [message.author] + message.mentions
    all_users_ids = map(lambda x: x.id, all_users)
    if not GlobalUserId.IdsExist(all_users_ids):
        for user in all_users:
            GlobalUserId.AddUserId(user, user.id)
            
    # Parse mentions: <@id> to @display_name
    other_texts = re.split(r"<.+>", content)
    metadata = re.findall(r"<.+>", content)
    metadata = map(convert_mention, metadata)
    
    if mention_flag:
        while True:
            pass
            
    
    


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

    postinitialization = ""
    def __init__(self, nome = None):
        self.SetName(nome)
    
    def SetName(self, nome = None):
        if nome is not None:
            self.postinitialization += f"\n\n$ Mensagem de {nome}:"
        else:
            self.postinitialization += "\n\n$ Mensagem do modelo: "
            
    def add_message(self, message: Message, username: str):
        self.chat_text += f"\n\n$ Mensagem de {username}: " + message.content + "\n"
    
    async def RecoverHistory(self, channel: TextChannel):
        print(f"Recovering history from channel {channel.name}")
        hist = channel.history(oldest_first=True)
        hist = [mes async for mes in hist]
        for message in hist[:-1]:
            self.add_message(message, str(message.author.display_name))
            
    # TODO: load chats from channel history

class ChatManager:
    channel_chat: dict
    
    def __init__(self):
        self.channel_chat = dict()
    
    async def add_channel(self, channel):
        if channel in self.channel_chat.keys():
            return self.channel_chat[channel]
        else:
            chat = self.channel_chat[channel] = Chat()
            await chat.RecoverHistory(channel)
        return chat

GlobalManager = ChatManager()