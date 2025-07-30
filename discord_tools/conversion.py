
import re
from discord import Message
from user_id import GlobalUserId, GlobalRoleId

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
          