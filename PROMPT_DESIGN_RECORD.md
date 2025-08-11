# Registro de Design de Prompt: RPG.AI-GEMINI-BOT-01

## 1. Metadados
**Propósito**: Gerenciar sessões de RPG de mesa via Discord, integrando sistema RAG para consultas D&D 5e com agente conversacional inteligente e sistema de contexto persistente via Redis.

**Modelo(s) Alvo**: Google Gemini 2.0 Flash Lite (otimizado para conversação e análise de contexto).

**Versão do Registro**: 1.0

**Sistema**: Bot Discord com múltiplos módulos especializados (RAG, RPG Agent, Context Manager).

## 2. Estrutura do Prompt

### 2.1 Chat RPG Principal
**Contexto de Entrada Necessário**: Lista de mensagens do chat, nome do bot, contexto Redis da sessão.

**Template do Prompt**: "Você é um modelo de linguagem conversando num chat de Discord. Seu objetivo principal é auxiliar a gerenciar uma sessão de RPG. Cite outros usuários utilizando @[nome-do-usuário]. Responda continuando a conversa de forma natural, continuando e contribuindo para a aventura com os jogadores."

### 2.2 Sistema RAG D&D
**Contexto de Entrada Necessário**: Chat com histórico, chunks relevantes de regras D&D, query do usuário.

**Template do Prompt**: "SEMPRE use as regras fornecidas acima para responder. Responda em português brasileiro. Seja direto e útil para Discord. Se há informação relevante nas regras, USE-A na resposta. Organize as informações de forma clara."

### 2.3 Análise de Contexto Redis
**Contexto de Entrada Necessário**: Mensagem do usuário, contexto atual da sessão (opcional).

**Template do Prompt**: "Você é um analisador especializado em sessões de RPG. Analise a mensagem abaixo e extraia informações importantes que devem ser armazenadas no contexto da sessão. Responda APENAS em formato JSON válido com a estrutura especificada."

### 2.4 Inicialização de História
**Contexto de Entrada Necessário**: Mensagens do chat para contexto, estado de inicialização da sessão.

**Template do Prompt**: "Você deverá criar a história do mundo com base nas informações dadas pelos usuários. Utilize a criatividade, visando criar uma partida de RPG engajante. Agora, utilize a ferramenta para escrever o esboço inicial da história do mundo."

## 3. Estrutura da Resposta

### 3.1 Chat RPG
**Intenção da Resposta**: Resposta conversacional natural que continua a narrativa RPG, citando usuários com @ e mantendo o contexto da aventura.

**Exemplo de Saída Ideal**: "Perfeito @Thorin! Como guerreiro anão, você consegue identificar que a caverna tem marcas de escavação recente. @Gandalf, você detecta uma aura mágica sutil vindo das profundezas. O que vocês querem fazer?"

### 3.2 RAG D&D
**Intenção da Resposta**: Resposta técnica baseada nas regras oficiais de D&D 5e, organizada e clara para uso no Discord.

**Exemplo de Saída Ideal**: "**Anões em D&D 5e:**\n\n🏔️ **Características Raciais:**\n- **Tendência:** Geralmente Leal e Bom\n- **Tamanho:** Médio (1,2-1,4m)\n- **Deslocamento:** 7,5 metros\n- **Visão no Escuro:** 18 metros"

### 3.3 Análise de Contexto
**Intenção da Resposta**: JSON estruturado com informações extraídas da mensagem para atualização automática do contexto Redis.

**Exemplo de Saída Ideal**: {"world_info": {"name": "Terra dos Anões", "type": "medieval"}, "characters": [{"name": "Thorin", "type": "player", "role": "guerreiro"}]}

## 4. Teste e Qualidade

### 4.1 Critérios de Aceite / Métricas de Qualidade

**Chat RPG:**
- ✅ **DEVE** responder em português brasileiro
- ✅ **DEVE** citar usuários com @[nome]
- ✅ **DEVE** continuar a narrativa naturalmente
- ✅ **NÃO DEVE** quebrar a imersão da sessão

**RAG D&D:**
- ✅ **DEVE** basear-se nas regras oficiais fornecidas
- ✅ **DEVE** responder em português brasileiro
- ✅ **DEVE** ser organizado e claro
- ✅ **DEVE** incluir informações relevantes dos chunks

**Análise de Contexto:**
- ✅ **DEVE** retornar JSON válido
- ✅ **DEVE** extrair informações relevantes
- ✅ **DEVE** manter estrutura consistente
- ✅ **NÃO DEVE** incluir texto explicativo

