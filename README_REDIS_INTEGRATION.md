# 🗄️ Sistema de Contexto Redis para RPG.AI-Gemini

## 📋 Visão Geral

Este sistema implementa um **gerenciador de contexto inteligente** usando Redis para manter informações importantes da sessão RPG em cache estruturado. Cada interação é analisada pelo Gemini para extrair e armazenar automaticamente:

- 🌍 **Informações do mundo** (nome, tipo, descrição)
- 👥 **Personagens** (jogadores e NPCs)
- 📍 **Localizações** importantes
- 🎯 **Quests** e objetivos
- ⚡ **Eventos** significativos
- 🔄 **Mudanças de estado** da sessão

## 🏗️ Arquitetura

```
Mensagem → Gemini Context Analyzer → Redis Context Store → Enhanced Prompts
    ↓              ↓                      ↓              ↓
Usuário    Extrai informações      Armazena contexto   Prompt rico
           importantes             estruturado         com contexto
```

### **Componentes Principais:**

1. **`RpgContext`** - Modelo de dados estruturado
2. **`ContextAnalyzer`** - Analisador usando Gemini
3. **`RedisContextManager`** - Gerenciador de persistência
4. **Integração com `RpgReasoner`** - Contexto nos prompts

## 🚀 Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Redis

#### **Opção A: Redis Local**
```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows (WSL ou Docker)
docker run -d -p 6379:6379 redis:alpine
```

#### **Opção B: Redis Cloud (Redis Labs)**
- Criar conta em [Redis Labs](https://redis.com/)
- Obter URL de conexão
- Configurar no `.env`

### 3. Variáveis de Ambiente
```bash
# .env
GOOGLE_API_KEY=sua_chave_gemini
DISCORD_TOKEN2=seu_token_discord
REDIS_URL=redis://localhost:6379  # ou URL do Redis Cloud
```

## 🎯 Como Funciona

### **1. Análise Automática de Contexto**
```python
# Cada mensagem é analisada pelo Gemini
extracted_info = analyzer.analyze_message_context(message, current_context)

# Informações extraídas automaticamente:
{
    "world_info": {"name": "Terra dos Anões", "type": "medieval"},
    "characters": [{"name": "Thorin", "type": "player", "role": "guerreiro"}],
    "locations": [{"name": "Ironforge", "is_current": True}],
    "quests": [{"name": "Tesouro Perdido", "status": "active"}],
    "events": [{"description": "Início da aventura", "importance": "high"}]
}
```

### **2. Armazenamento Estruturado no Redis**
```python
# Chaves Redis organizadas:
rpg:session:{session_id}     # Dados da sessão
rpg:channel:{channel_id}     # Mapeamento canal→sessão

# TTL automático de 24 horas
# Persistência entre reinicializações
```

### **3. Contexto Enriquecido nos Prompts**
```python
# Antes (sem contexto):
prompt = "Você é um mestre de RPG..."

# Depois (com contexto):
prompt = f"""Você é um mestre de RPG...

📋 **CONTEXTO DA SESSÃO:**
🌍 **Mundo**: Terra dos Anões
🎭 **Tipo**: medieval
📍 **Localização Atual**: Ironforge
🎯 **Quest Atual**: Tesouro Perdido
👥 **Jogadores**: Thorin
⚡ **Eventos Importantes**: Início da aventura

Continue a narrativa..."""
```

## 🔧 Uso no Código

### **Integração Automática**
```python
# O sistema funciona automaticamente:
reasoner = RpgReasoner(channel_id)
# ↑ Contexto Redis integrado automaticamente

# Cada mensagem atualiza o contexto:
reasoner.GenerateRequest(chat, model)
# ↑ Analisa, extrai e armazena informações
```

### **Acesso Manual ao Contexto**
```python
from rpg_tools.context_manager import context_manager

# Obter contexto de um canal
context = context_manager.get_session(channel_id)

# Resumo para prompts
summary = context_manager.get_context_summary(channel_id)

# Atualizar manualmente
context_manager.update_context(channel_id, message, username)
```

## 📊 Estrutura de Dados

### **RpgContext**
```python
class RpgContext:
    # Identificação
    session_id: str
    channel_id: str
    channel_name: str
    
    # Mundo
    world_name: Optional[str]
    world_type: Optional[str]
    world_description: Optional[str]
    
    # Personagens
    player_characters: List[Dict]
    npcs: List[Dict]
    
    # Estado da aventura
    current_location: Optional[str]
    current_quest: Optional[str]
    completed_quests: List[str]
    
    # Histórico
    key_events: List[Dict]
    world_history: Optional[str]
    
    # Metadados
    created_at: datetime
    last_updated: datetime
    session_state: str
    game_system: str
    difficulty_level: str
```

## 🧪 Testando o Sistema

### **1. Teste Básico**
```bash
python test_context_system.py
```

### **2. Teste de Integração**
```bash
python test_rpg_rag_integration.py
```

### **3. Verificar Redis**
```bash
redis-cli
> KEYS rpg:*
> GET rpg:channel:123456789
> GET rpg:session:123456789_1234567890
```

## 🎮 Exemplos de Uso

### **Exemplo 1: Criação de Mundo**
```
Usuário: @bot Vamos criar um mundo cyberpunk chamado "Neo Tokyo"
Bot: [Analisa e armazena no Redis]
     [Resposta enriquecida com contexto]
```

### **Exemplo 2: Adição de Personagem**
```
Usuário: @bot Meu personagem é um hacker chamado "Shadow"
Bot: [Analisa e armazena no Redis]
     [Resposta contextualizada]
```

### **Exemplo 3: Mudança de Localização**
```
Usuário: @bot Agora estamos no distrito de Shibuya
Bot: [Analisa e atualiza localização no Redis]
     [Resposta com contexto atualizado]
```

## 🔍 Benefícios

### **1. Memória Persistente**
- ✅ Contexto mantido entre reinicializações
- ✅ Sessões compartilhadas entre instâncias
- ✅ Histórico estruturado e pesquisável

### **2. Análise Inteligente**
- ✅ Gemini extrai informações automaticamente
- ✅ Contexto sempre atualizado
- ✅ Prompts enriquecidos e relevantes

### **3. Performance**
- ✅ Cache Redis em memória (rápido)
- ✅ TTL automático (limpeza automática)
- ✅ Estrutura otimizada para consultas

### **4. Escalabilidade**
- ✅ Múltiplos canais simultâneos
- ✅ Sessões independentes
- ✅ Fácil backup e replicação

## 🐛 Solução de Problemas

### **Redis não conecta**
```bash
# Verificar se Redis está rodando
redis-cli ping
# Deve retornar PONG

# Verificar configuração
echo $REDIS_URL
# Deve mostrar URL válida
```

### **Erro de análise de contexto**
```bash
# Verificar GOOGLE_API_KEY
echo $GOOGLE_API_KEY
# Deve mostrar chave válida

# Verificar logs do Gemini
# Pode ser limite de rate ou chave inválida
```

### **Contexto não persiste**
```bash
# Verificar TTL no Redis
redis-cli TTL rpg:session:session_id
# Deve ser > 0

# Verificar se chaves existem
redis-cli KEYS rpg:*
```

## 🔮 Próximos Passos

1. **Sistema de Backup** - Persistir contexto em banco relacional
2. **Análise Avançada** - Machine learning para extração de contexto
3. **Integração com APIs** - D&D Beyond, Roll20, etc.
4. **Interface Web** - Visualização e edição de contexto
5. **Sincronização** - Compartilhar contexto entre servidores

## 📚 Referências

- [Redis Documentation](https://redis.io/documentation)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)
- [Google Generative AI](https://ai.google.dev/)
- [Discord.py](https://discordpy.readthedocs.io/)

## 🤝 Contribuindo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** com testes
4. **Commit** suas mudanças
5. **Push** e abra um Pull Request

---

**🎮 Com o sistema de contexto Redis, seu bot RPG agora tem memória persistente e inteligente!**
