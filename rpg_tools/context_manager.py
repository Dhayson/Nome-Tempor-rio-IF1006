#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Contexto RPG usando Redis
Mantém informações importantes da sessão em cache estruturado
"""

import json
import redis
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente
load_dotenv()

class RpgContext(BaseModel):
    """Modelo de dados para contexto RPG"""
    session_id: str = Field(..., description="ID único da sessão")
    channel_id: str = Field(..., description="ID do canal Discord")
    channel_name: str = Field(..., description="Nome do canal")
    
    # Informações do mundo
    world_name: Optional[str] = Field(None, description="Nome do mundo")
    world_type: Optional[str] = Field(None, description="Tipo de mundo (medieval, cyberpunk, etc.)")
    world_description: Optional[str] = Field(None, description="Descrição geral do mundo")
    
    # Personagens principais
    player_characters: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de personagens dos jogadores")
    npcs: List[Dict[str, Any]] = Field(default_factory=list, description="NPCs importantes")
    
    # Estado da aventura
    current_location: Optional[str] = Field(None, description="Localização atual dos jogadores")
    current_quest: Optional[str] = Field(None, description="Quest atual")
    completed_quests: List[str] = Field(default_factory=list, description="Quests completadas")
    
    # Histórico e eventos
    key_events: List[Dict[str, Any]] = Field(default_factory=list, description="Eventos importantes da sessão")
    world_history: Optional[str] = Field(None, description="História geral do mundo")
    
    # Metadados
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação da sessão")
    last_updated: datetime = Field(default_factory=datetime.now, description="Última atualização")
    session_state: str = Field("active", description="Estado da sessão (active, paused, completed)")
    
    # Configurações
    game_system: str = Field("D&D 5e", description="Sistema de RPG")
    difficulty_level: str = Field("medium", description="Nível de dificuldade")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ContextAnalyzer:
    """Analisador de contexto usando Gemini para extrair informações importantes"""
    
    def __init__(self, api_key: str = None):
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    def analyze_message_context(self, message: str, current_context: Optional[RpgContext] = None) -> Dict[str, Any]:
        """
        Analisa uma mensagem para extrair informações importantes do contexto RPG
        
        Args:
            message: Mensagem do usuário
            current_context: Contexto atual da sessão
            
        Returns:
            Dicionário com informações extraídas
        """
        # Construir prompt para análise
        context_info = ""
        if current_context:
            context_info = f"""
CONTEXTO ATUAL:
- Mundo: {current_context.world_name or 'Não definido'}
- Tipo: {current_context.world_type or 'Não definido'}
- Localização: {current_context.current_location or 'Não definida'}
- Quest atual: {current_context.current_quest or 'Nenhuma'}
- Personagens: {len(current_context.player_characters)} jogadores, {len(current_context.npcs)} NPCs
"""
        
        prompt = f"""Você é um analisador especializado em sessões de RPG. Analise a mensagem abaixo e extraia informações importantes que devem ser armazenadas no contexto da sessão.

{context_info}

MENSAGEM: {message}

ANALISE E EXTRAIA:
1. Informações sobre o mundo (nome, tipo, descrição)
2. Personagens mencionados (jogadores ou NPCs)
3. Localizações mencionadas
4. Quests ou objetivos
5. Eventos importantes
6. Mudanças de estado da sessão

Responda APENAS em formato JSON válido com a seguinte estrutura:
{{
    "world_info": {{
        "name": "string ou null",
        "type": "string ou null", 
        "description": "string ou null"
    }},
    "characters": [
        {{
            "name": "string",
            "type": "player ou npc",
            "description": "string ou null",
            "role": "string ou null"
        }}
    ],
    "locations": [
        {{
            "name": "string",
            "description": "string ou null",
            "is_current": boolean
        }}
    ],
    "quests": [
        {{
            "name": "string",
            "description": "string ou null",
            "status": "active, completed, ou failed"
        }}
    ],
    "events": [
        {{
            "description": "string",
            "importance": "high, medium, ou low",
            "timestamp": "string ISO"
        }}
    ],
    "session_changes": {{
        "state_change": "string ou null",
        "difficulty_change": "string ou null"
    }}
}}

Se não houver informações relevantes em alguma categoria, use null ou lista vazia."""

        try:
            response = self.model.generate_content(prompt)
            # Tentar extrair JSON da resposta
            response_text = response.text.strip()
            
            # Remover markdown se presente
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            # Parsear JSON
            extracted_info = json.loads(response_text)
            return extracted_info
            
        except Exception as e:
            print(f"Erro ao analisar contexto: {e}")
            # Retornar estrutura vazia em caso de erro
            return {
                "world_info": {"name": None, "type": None, "description": None},
                "characters": [],
                "locations": [],
                "quests": [],
                "events": [],
                "session_changes": {"state_change": None, "difficulty_change": None}
            }

class RedisContextManager:
    """Gerenciador de contexto usando Redis"""
    
    def __init__(self, redis_url: str = None):
        if not redis_url:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.analyzer = ContextAnalyzer()
        
        # Prefixos para chaves Redis
        self.session_prefix = "rpg:session:"
        self.channel_prefix = "rpg:channel:"
        self.global_prefix = "rpg:global:"
    
    def _get_session_key(self, session_id: str) -> str:
        """Gera chave Redis para uma sessão"""
        return f"{self.session_prefix}{session_id}"
    
    def _get_channel_key(self, channel_id: str) -> str:
        """Gera chave Redis para um canal"""
        return f"{self.channel_prefix}{channel_id}"
    
    def create_session(self, channel_id: str, channel_name: str) -> str:
        """
        Cria uma nova sessão RPG
        
        Args:
            channel_id: ID do canal Discord
            channel_name: Nome do canal
            
        Returns:
            ID da sessão criada
        """
        session_id = f"{channel_id}_{int(datetime.now().timestamp())}"
        
        # Criar contexto inicial
        context = RpgContext(
            session_id=session_id,
            channel_id=channel_id,
            channel_name=channel_name
        )
        
        # Salvar no Redis
        session_key = self._get_session_key(session_id)
        self.redis_client.setex(
            session_key,
            timedelta(hours=24),  # TTL de 24 horas
            context.model_dump_json()
        )
        
        # Mapear canal para sessão
        channel_key = self._get_channel_key(channel_id)
        self.redis_client.setex(
            channel_key,
            timedelta(hours=24),
            session_id
        )
        
        print(f"✅ Nova sessão RPG criada: {session_id}")
        return session_id
    
    def get_session(self, channel_id: str) -> Optional[RpgContext]:
        """
        Recupera a sessão ativa de um canal
        
        Args:
            channel_id: ID do canal Discord
            
        Returns:
            Contexto da sessão ou None se não existir
        """
        channel_key = self._get_channel_key(channel_id)
        session_id = self.redis_client.get(channel_key)
        
        if not session_id:
            return None
        
        session_key = self._get_session_key(session_id)
        session_data = self.redis_client.get(session_key)
        
        if not session_data:
            return None
        
        try:
            context_dict = json.loads(session_data)
            # Converter timestamps de volta para datetime
            for field in ['created_at', 'last_updated']:
                if field in context_dict and context_dict[field]:
                    context_dict[field] = datetime.fromisoformat(context_dict[field])
            
            return RpgContext(**context_dict)
        except Exception as e:
            print(f"Erro ao carregar contexto: {e}")
            return None
    
    def update_context(self, channel_id: str, message: str, username: str) -> RpgContext:
        """
        Atualiza o contexto da sessão com uma nova mensagem
        
        Args:
            channel_id: ID do canal Discord
            message: Mensagem do usuário
            username: Nome do usuário
            
        Returns:
            Contexto atualizado
        """
        # Recuperar ou criar sessão
        context = self.get_session(channel_id)
        if not context:
            context = RpgContext(
                session_id=self.create_session(channel_id, "Unknown"),
                channel_id=channel_id,
                channel_name="Unknown"
            )
        
        # Analisar mensagem com Gemini
        extracted_info = self.analyzer.analyze_message_context(message, context)
        
        # Atualizar contexto com informações extraídas
        context = self._merge_extracted_info(context, extracted_info, username)
        
        # Salvar contexto atualizado
        self._save_context(context)
        
        return context
    
    def _merge_extracted_info(self, context: RpgContext, extracted_info: Dict[str, Any], username: str) -> RpgContext:
        """Mescla informações extraídas com o contexto existente"""
        
        # Atualizar informações do mundo
        if extracted_info.get("world_info"):
            world_info = extracted_info["world_info"]
            if world_info.get("name") and not context.world_name:
                context.world_name = world_info["name"]
            if world_info.get("type") and not context.world_type:
                context.world_type = world_info["type"]
            if world_info.get("description") and not context.world_description:
                context.world_description = world_info["description"]
        
        # Adicionar novos personagens
        for char_info in extracted_info.get("characters", []):
            char_name = char_info.get("name")
            if char_name and not any(c.get("name") == char_name for c in context.player_characters + context.npcs):
                if char_info.get("type") == "player":
                    context.player_characters.append({
                        "name": char_name,
                        "description": char_info.get("description"),
                        "role": char_info.get("role"),
                        "added_by": username,
                        "added_at": datetime.now().isoformat()
                    })
                else:
                    context.npcs.append({
                        "name": char_name,
                        "description": char_info.get("description"),
                        "role": char_info.get("role"),
                        "added_by": username,
                        "added_at": datetime.now().isoformat()
                    })
        
        # Adicionar novas localizações
        for loc_info in extracted_info.get("locations", []):
            loc_name = loc_info.get("name")
            if loc_name:
                # Verificar se já existe
                existing_locations = [loc for loc in context.key_events if loc.get("type") == "location"]
                if not any(loc.get("name") == loc_name for loc in existing_locations):
                    context.key_events.append({
                        "type": "location",
                        "name": loc_name,
                        "description": loc_info.get("description"),
                        "is_current": loc_info.get("is_current", False),
                        "added_by": username,
                        "added_at": datetime.now().isoformat()
                    })
                    
                    # Atualizar localização atual se especificado
                    if loc_info.get("is_current"):
                        context.current_location = loc_name
        
        # Adicionar novas quests
        for quest_info in extracted_info.get("quests", []):
            quest_name = quest_info.get("name")
            if quest_name and not any(q.get("name") == quest_name for q in context.key_events if q.get("type") == "quest"):
                context.key_events.append({
                    "type": "quest",
                    "name": quest_name,
                    "description": quest_info.get("description"),
                    "status": quest_info.get("status", "active"),
                    "added_by": username,
                    "added_at": datetime.now().isoformat()
                })
                
                # Atualizar quest atual se for ativa
                if quest_info.get("status") == "active":
                    context.current_quest = quest_name
        
        # Adicionar novos eventos
        for event_info in extracted_info.get("events", []):
            event_desc = event_info.get("description")
            if event_desc:
                context.key_events.append({
                    "type": "event",
                    "description": event_desc,
                    "importance": event_info.get("importance", "medium"),
                    "added_by": username,
                    "added_at": datetime.now().isoformat()
                })
        
        # Atualizar metadados
        context.last_updated = datetime.now()
        
        return context
    
    def _save_context(self, context: RpgContext):
        """Salva contexto no Redis"""
        session_key = self._get_session_key(context.session_id)
        self.redis_client.setex(
            session_key,
            timedelta(hours=24),
            context.model_dump_json()
        )
    
    def get_context_summary(self, channel_id: str) -> str:
        """
        Gera um resumo do contexto para usar nos prompts
        
        Args:
            channel_id: ID do canal Discord
            
        Returns:
            Resumo formatado do contexto
        """
        context = self.get_session(channel_id)
        if not context:
            return "Nenhuma sessão RPG ativa neste canal."
        
        summary_parts = []
        
        # Informações básicas
        if context.world_name:
            summary_parts.append(f"🌍 **Mundo**: {context.world_name}")
        if context.world_type:
            summary_parts.append(f"🎭 **Tipo**: {context.world_type}")
        if context.current_location:
            summary_parts.append(f"📍 **Localização Atual**: {context.current_location}")
        if context.current_quest:
            summary_parts.append(f"🎯 **Quest Atual**: {context.current_quest}")
        
        # Personagens
        if context.player_characters:
            pc_names = [pc["name"] for pc in context.player_characters]
            summary_parts.append(f"👥 **Jogadores**: {', '.join(pc_names)}")
        
        if context.npcs:
            npc_names = [npc["name"] for npc in context.npcs]
            summary_parts.append(f"🤖 **NPCs**: {', '.join(npc_names)}")
        
        # Eventos importantes
        important_events = [e for e in context.key_events if e.get("importance") == "high"]
        if important_events:
            event_descriptions = [e["description"] for e in important_events[-3:]]  # Últimos 3 eventos importantes
            summary_parts.append(f"⚡ **Eventos Importantes**: {'; '.join(event_descriptions)}")
        
        # Histórico do mundo
        if context.world_history:
            summary_parts.append(f"📚 **História**: {context.world_history[:200]}...")
        
        if not summary_parts:
            return "Sessão RPG criada, aguardando informações do mundo."
        
        return "\n".join(summary_parts)
    
    def cleanup_expired_sessions(self):
        """Remove sessões expiradas do Redis"""
        try:
            # Redis automaticamente remove chaves com TTL expirado
            # Mas podemos fazer uma limpeza manual se necessário
            print("🧹 Limpeza automática de sessões expiradas (TTL)")
        except Exception as e:
            print(f"Erro na limpeza: {e}")

# Instância global
context_manager = RedisContextManager()
