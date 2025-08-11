# 🎮 RPG.AI-Gemini - Integração Completa

## 📋 Visão Geral

Este projeto integra um **sistema RAG (Retrieval-Augmented Generation)** especializado em Dungeons & Dragons 5e com um **agente de IA conversacional** para criar um bot Discord inteligente que pode:

1. **Responder perguntas sobre regras D&D** usando o sistema RAG
2. **Gerenciar sessões de RPG** usando o agente conversacional
3. **Automaticamente escolher** entre RAG e RPG baseado no contexto

## 🏗️ Arquitetura da Integração

### Sistema Unificado (`rpg_ai_integrated.py`)
- **Bot Discord principal** que combina ambos os sistemas
- **Roteamento inteligente** de mensagens
- **Fallback automático** entre sistemas

### Sistema RAG (`rag.py`)
- **Base de conhecimento** D&D 5e
- **Busca vetorial** usando FAISS
- **Geração de respostas** com Gemini
- **Tradução automática** PT-EN

### Agente RPG (`rpg_tools/`)
- **Gerenciamento de sessões** de RPG
- **Ferramentas especializadas** (dados, história, inicialização)
- **Estados de conversa** (inicialização, world-building, conversa)

## 🚀 Como Usar

### 1. Configuração
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves:
# GOOGLE_API_KEY=sua_chave_gemini
# DISCORD_TOKEN2=seu_token_discord
```

### 2. Executar o Bot Integrado
```bash
python rpg_ai_integrated.py
```

### 3. Testar a Integração
```bash
# Testar sistema RAG
python test_rag_integration.py

# Testar integração RPG+RAG
python test_rpg_rag_integration.py
```

## 🎯 Funcionalidades

### Sistema RAG (Consultas D&D)
- **Perguntas sobre regras**: "Como funcionam os Anões?"
- **Consultas de mecânicas**: "Qual é a AC dos elfos?"
- **Explicações de conceitos**: "O que é vantagem e desvantagem?"

### Agente RPG (Gerenciamento de Sessões)
- **Inicialização de RPG**: `!help` para comandos
- **Rolagem de dados**: D20 automático
- **História do mundo**: Criação e expansão
- **Conversa natural**: Respostas contextuais

### Roteamento Inteligente
O bot **automaticamente decide** qual sistema usar:

```
Mensagem → Análise → RAG ou RPG?
├── Se contém termos D&D → Sistema RAG
├── Se é comando RPG → Agente RPG
└── Se é conversa geral → Agente RPG
```

## 🔧 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `rpg_ai_integrated.py` | **Bot principal integrado** |
| `rag.py` | Sistema RAG D&D |
| `rpg_tools/reasoner.py` | Agente RPG com integração RAG |
| `discord_tools/` | Ferramentas Discord |
| `test_*.py` | Testes de integração |

## 📊 Fluxo de Funcionamento

```
1. Usuário menciona o bot
2. Bot analisa a mensagem
3. Decisão automática:
   ├── RAG: Para perguntas D&D
   └── RPG: Para conversa/RPG
4. Geração de resposta
5. Envio para Discord
```

## 🧪 Testando a Integração

### Teste RAG
```python
from rag import get_rag_system
rag = get_rag_system()
response = rag.generate_answer(chat, "Como funcionam os Anões?")
```

### Teste RPG
```python
from rpg_tools.reasoner import RpgReasoner
reasoner = RpgReasoner()
responses = reasoner.GenerateRequest(chat, model)
```

### Teste Integrado
```python
# O bot automaticamente escolhe o sistema correto
# baseado no conteúdo da mensagem
```

## 🐛 Solução de Problemas

### Erro de Importação
```bash
# Verificar se todos os módulos estão instalados
pip install -r requirements.txt

# Verificar se o ambiente virtual está ativo
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### Sistema RAG não inicializa
- Verificar se `dnd.txt` existe
- Verificar se `GOOGLE_API_KEY` está configurada
- Verificar permissões de arquivo

### Bot Discord não conecta
- Verificar se `DISCORD_TOKEN2` está correto
- Verificar se o bot tem permissões no servidor
- Verificar se as intents estão habilitadas

## 🔮 Próximos Passos

1. **Melhorar detecção** de contexto D&D vs RPG
2. **Adicionar mais ferramentas** RPG (mapas, NPCs, etc.)
3. **Sistema de cache** para respostas RAG
4. **Interface web** para configuração
5. **Múltiplos idiomas** além de PT/EN

## 📝 Exemplos de Uso

### Consulta D&D (RAG)
```
Usuário: @bot Como funcionam os Anões em D&D?
Bot: [Resposta baseada nas regras oficiais]
```

### Comando RPG (Agente)
```
Usuário: !help
Bot: [Lista de comandos RPG disponíveis]
```

### Conversa RPG (Agente)
```
Usuário: @bot Vamos começar uma aventura!
Bot: [Inicia processo de criação de mundo]
```

## 🤝 Contribuindo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra** um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.
