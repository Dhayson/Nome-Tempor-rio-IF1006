from rpg_tools.agentic_tools.dice import D20_tool_explanation, D20_tool

Tool_list = [D20_tool]

All_tools_explanation = f"Você tem acesso a algumas ferramentas, que deve chamar exatamente quando for necessãrio\n\n" + \
"\n".join([D20_tool_explanation]) + "\n"