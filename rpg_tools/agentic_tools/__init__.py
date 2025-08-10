from rpg_tools.agentic_tools.dice import D20_tool_explanation, D20_tool
from rpg_tools.agentic_tools.rpg_init import Init_RPG_tool, Init_RPG_tool_explanation

class ToolSettings:
    Conversation_tool_list = {"D20": D20_tool, "InitRPG": Init_RPG_tool}
    Explanation_tool_list = {"D20": D20_tool_explanation, "InitRPG": Init_RPG_tool_explanation}
    
    def __init__(self):
        pass
    
    def get_conversation_tools_explanation(self):
        return f"Você tem acesso a algumas ferramentas, que deve chamar exatamente quando for necessãrio\n\n" + \
    "\n".join(list(self.Explanation_tool_list.values())) + "\n"
    
    def get_tool_list(self):
        return list(self.Conversation_tool_list.values())
    
    def add_tool(self, key, tool, tool_explanation):
        self.Conversation_tool_list[key] = tool
        self.Explanation_tool_list[key] = tool_explanation
        
    def remove_tool(self, key):
        tool = self.Conversation_tool_list.pop(key)
        explanation = self.Explanation_tool_list.pop(key)
        return (tool, explanation)
    
Global_tool_settings = ToolSettings()
