# 🚀 Deploy RPG.AI-Gemini no Railway

Este guia explica como fazer o deploy do bot RPG.AI-Gemini no Railway.

## 📋 Pré-requisitos

1. **Conta no Railway**: Crie uma conta em [railway.app](https://railway.app)
2. **API Key do Google Gemini**: Obtenha em [Google AI Studio](https://aistudio.google.com/app/apikey)
3. **Bot Discord**: Crie um bot em [Discord Developer Portal](https://discord.com/developers/applications)

## 🔧 Configuração das Variáveis de Ambiente

No Railway, configure as seguintes variáveis de ambiente:

### Obrigatórias:
- `GOOGLE_API_KEY`: Sua chave da API do Google Gemini
- `DISCORD_TOKEN`: Token do seu bot Discord

### Opcionais:
- `REDIS_URL`: URL do Redis (Railway pode fornecer automaticamente)

## 📦 Arquivos de Deploy

Os seguintes arquivos são necessários para o deploy (já incluídos):

- `Procfile`: Define como executar a aplicação
- `runtime.txt`: Especifica a versão do Python
- `requirements.txt`: Lista as dependências
- `env.example`: Exemplo de configuração das variáveis

## 🚀 Passos para Deploy

### 1. Preparar o Repositório
```bash
# Certifique-se de que todos os arquivos estão commitados
git add .
git commit -m "Preparar para deploy no Railway"
git push
```

### 2. Configurar no Railway
1. Acesse [railway.app](https://railway.app)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Railway detectará automaticamente o Python

### 3. Configurar Variáveis de Ambiente
1. Vá para a aba "Variables"
2. Adicione as variáveis obrigatórias:
   - `GOOGLE_API_KEY`
   - `DISCORD_TOKEN`

### 4. Configurar Redis (Opcional)
1. Adicione um serviço Redis no Railway
2. Railway automaticamente configurará `REDIS_URL`

### 5. Deploy
1. Railway fará o deploy automaticamente
2. Monitore os logs para verificar se está funcionando
3. O bot estará online quando aparecer "🤖 Bot [nome] está online!"

## 🔍 Verificação

Para verificar se o deploy funcionou:

1. **Logs**: Verifique os logs no Railway
2. **Discord**: O bot deve aparecer online no seu servidor
3. **Teste**: Mencione o bot em um canal para testar

## 🐛 Solução de Problemas

### Bot não responde:
- Verifique se `DISCORD_TOKEN` está correto
- Confirme se o bot tem permissões no servidor
- Verifique se `message_content` intent está habilitado

### Erro de API Gemini:
- Verifique se `GOOGLE_API_KEY` está correto
- Confirme se a API está habilitada no Google Cloud

### Erro de dependências:
- Verifique se `requirements.txt` está completo
- Confirme se a versão do Python em `runtime.txt` é suportada

## 📱 Comandos do Bot

O bot responde quando mencionado (@bot) e suporta:

- 🎲 **Conversas RPG**: Narrativa interativa com dados
- 📚 **Consultas D&D**: Perguntas sobre regras usando RAG
- 🌍 **Criação de mundo**: Ferramentas para world building
- 💾 **Contexto persistente**: Histórico salvo no Redis

## 🔄 Atualizações

Para atualizar o bot:
1. Faça push das mudanças no GitHub
2. Railway fará redeploy automaticamente
3. Monitor os logs durante a atualização
