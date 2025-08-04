from rpg_tools.agentic_tools.dice import D20_tool_explanation, D20_tool
from rpg_tools.agentic_tools.rpg_init import Init_RPG_tool, Init_RPG_tool_explanation

Conversation_tool_list = [D20_tool, Init_RPG_tool]

Conversation_tools_explanation = f"Você tem acesso a algumas ferramentas, que deve chamar exatamente quando for necessãrio\n\n" + \
"\n".join([D20_tool_explanation, Init_RPG_tool_explanation]) + "\n"