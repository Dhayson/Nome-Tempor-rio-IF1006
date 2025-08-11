import google.ai.generativelanguage as glm

WorldHistoryTool_glm = glm.FunctionDeclaration(
    name = "InicializarHistoria",
    # OBSERVAÇÃO: Isso não está no formato correto
    description = "Escreve o esboço inicial da história da partida de rpg",
    parameters = glm.Schema(
        type = glm.Type.OBJECT,
        properties = {
            "history_text": glm.Schema(
                type = glm.Type.STRING,
                description = "Corpo principal da história. É essencial que possua todos os detalhes principais do mundo da aventura de RPG."
            )
        },
        required = ["history_text"],
    ),
)


WorldHistoryTool_explanation = """Agora, você deve chamar a função InicializarHistória com um texto sobre a história \
do mundo de RPG da partida que está sendo inicializada.

"""



AddHistoryTool_glm = glm.FunctionDeclaration(
    name = "ExpandirHistoria",
    # OBSERVAÇÃO: Isso não está no formato correto
    description = "Adiciona informações a história",
    parameters = glm.Schema(
        type = glm.Type.OBJECT,
        properties = {
            "history_text": glm.Schema(
                type = glm.Type.STRING,
                description = "Acrescenta informações à história, baseado nos últimos desenvolvimentos. Resuma brevemente para formar um texto conciso."
            )
        },
        required = ["history_text"],
    ),
)

AddHistoryTool_explanation = """Chame de vez em quando a função de ExpandirHistória \
Ela serve para adicionar breves informações à história no mundo, conforme é desvendada pelos jogadores.

"""

AddHistoryTool_explanation_alt = """Agora você deve chamar a função de ExpandirHistória \
Ela serve para adicionar breves informações à história no mundo, conforme é desvendada pelos jogadores. \
Agora chame essa função
"""

class WorldHistoryTool:
    main_text = ""
    
    def GetHistory(self):
        if self.main_text == "":
            return "No momento, a seção de RPG não está ativa, mas, você ainda pode tirar dúvidas, conversar com os jogadores e auxiliar a inicializar uma seção\n"
        else:
            return self.main_text
        
    def WriteHistory(self, history_text):
        self.main_text = """ No momento, a seção de RPG está ativa. Deve-se continuar desenvolvendo a história \
com base nesse resumo. Futuramente, conforme o desenrolar da narrativa, serão adicionadas novas informações.
Não tente iniciar novamente a aventura.
Agora segue aqui a história desse mundo: """ + history_text
        print(f"HISTÓRIA ESCRITA")
        print(self.main_text)
        return f"\\ História do mundo: {history_text}"
    
    def AddHistory(self, history_text):
        print(f"HISTÓRIA ESCRITA")
        print(history_text)
        self.main_text += history_text
        return f"\\ {history_text}"