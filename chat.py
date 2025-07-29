from discord import TextChannel, Message
from user_id import GlobalUserId, GlobalRoleId
import re, datetime

def convert_mention(mention: str):
    if not re.match("<@[0-9]+>$", mention):
        return mention
    id = int(mention[2:-1])
    return f"@{GlobalUserId.GetUser(id).display_name}"

def convert_role_mention(mention: str):
    if not re.match("<@&[0-9]+>$", mention):
        return mention
    id = int(mention[3:-1])
    return f"@role_{GlobalRoleId.GetRole(id).name}"
    

def parse_message(message: Message):
    content = message.content
    if content is None or content == "":
        return ""
    mention_flag = content[0] == '<'
    
    # Add users and their ids to the mapping, if at least one is missing
    guild = message.guild
    guild_users = []
    if guild:
        guild_users = list(guild.members)
    all_users = [message.author] + message.mentions + message.channel.members + guild_users
    all_users_ids = map(lambda x: x.id, all_users)
    if not GlobalUserId.IdsExist(all_users_ids):
        for user in all_users:
            GlobalUserId.AddUserId(user, user.id)
    
    all_roles_ids = map(lambda x: x.id, message.guild.roles)
    if not GlobalRoleId.IdsExist(all_roles_ids):
        for role in message.guild.roles:
            GlobalRoleId.AddRoleId(role, role.id)
    
            
    # Parse mentions: <@id> to @display_name
    other_texts = iter(re.split(r"<.+>", content))
    metadata = re.findall(r"<.+>", content)
    metadata = map(convert_mention, metadata)
    metadata = map(convert_role_mention, metadata)
    
    final_text: str = ""
    if mention_flag:
        # If the message starts with a mention
        while True:
            next1 = next(metadata, None)
            if next1:
                final_text += next1
            next2 = next(other_texts, None)
            if next2:
                final_text += next2
            if next1 is None and next2 is None:
                break
    else:
        # If the message does not start with a mention
        while True:
            next1 = next(other_texts, None)
            if next1:
                final_text += next1
            next2 = next(metadata, None)
            if next2:
                final_text += next2
            if next1 is None and next2 is None:
                break
    
    return final_text
            
    
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
    
    def SetName(self, nome = None, timestamp = True):
        if nome is not None:
            self.postinitialization = lambda:  f"\n\n$ Mensagem de {nome}:"
        elif timestamp:
            self.postinitialization = lambda: f"\n\n$ Mensagem de {nome} às {datetime.datetime.now()}:"
        else:
            self.postinitialization = lambda: "\n\n$ Mensagem do modelo: "
            
    def add_message(self, message: Message, username: str):
        self.messages.append(ChatMessage(message, message.created_at, username))
        new_message = f"$ Mensagem de {username} às {message.created_at}: " + parse_message(message) + "\n\n\n"
        print(f"{message.channel}|{username}|{message.author.id}:\n", new_message)
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
        if channel in self.channel_chat.keys():
            return self.channel_chat[channel]
        else:
            chat = self.channel_chat[channel] = Chat()
            await chat.RecoverHistory(channel)
        return chat

GlobalManager = ChatManager()