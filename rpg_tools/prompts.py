from discord_tools.chat import ChatMessage, parse_message
import datetime

LLM_NAME: str = "LLM"

preinit = """Você é um modelo de linguagem conversando num chat de Discord
Seu objetivo principal é auxiliar a gerenciar uma sessão de RPG
Cite outros usuários utilizando @[nome-do-usuário]
Responda continuando a conversa de forma natural, continuando e contribuindo para a aventura com os jogadores

"""

def chatBuild(messages: list[ChatMessage]):
    chat_text = map(lambda x: f"$ Mensagem de {x.username} às {x.time}: " + parse_message(x.discord_message) + "\n$$$", messages)
    chat_text = "\n".join(chat_text)
    final_text = f"""As mensagens anteriores são sinalizadas com [ $ Mensagem de x: ] e  [ $ Mensagem do modelo: ] terminando com $$$
Agora seguem as mensagens:
{chat_text}

"""
    return final_text

postinit = lambda: f"\n\n$ Mensagem de {LLM_NAME} às {datetime.datetime.now()}: "

postinit_alt = lambda: f"\n\nFIM DAS MENSAGENS\n"

preinit_create_history = """Você é um modelo de linguagem conversando num chat de Discord
Seu objetivo principal é auxiliar a gerenciar uma sessão de RPG
Agora, você deverá criar a história do mundo com base nas informações dadas pelos usuários.
Utilize a criatividade, visando criar uma partida de RPG engajante.

"""

postinit_create_history = """Agora, utilize a ferramenta para escrever o esboço inicial da história do mundo."""
