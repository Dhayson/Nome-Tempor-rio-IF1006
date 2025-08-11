#!/usr/bin/env python3
"""
Teste do sistema de contexto Redis para RPG
"""

import sys
import os
import asyncio

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_context_system():
    """Testa o sistema de contexto Redis"""
    print("🧪 Testando Sistema de Contexto Redis")
    print("=" * 50)
    
    try:
        # Testar importação do sistema de contexto
        from rpg_tools.context_manager import context_manager, RpgContext
        print("✅ Sistema de contexto importado com sucesso")
        
        # Testar criação de contexto
        print("\n📝 Testando criação de contexto...")
        test_channel_id = "123456789"
        test_channel_name = "test-channel"
        
        session_id = context_manager.create_session(test_channel_id, test_channel_name)
        print(f"✅ Sessão criada: {session_id}")
        
        # Testar recuperação de contexto
        print("\n📖 Testando recuperação de contexto...")
        context = context_manager.get_session(test_channel_id)
        if context:
            print(f"✅ Contexto recuperado: {context.session_id}")
            print(f"   Canal: {context.channel_name}")
            print(f"   Criado em: {context.created_at}")
        else:
            print("❌ Falha ao recuperar contexto")
            return False
        
        # Testar atualização de contexto
        print("\n🔄 Testando atualização de contexto...")
        test_message = "Vamos criar um mundo medieval chamado 'Terra dos Anões' com uma cidade chamada 'Ironforge'"
        test_username = "TestUser"
        
        updated_context = context_manager.update_context(test_channel_id, test_message, test_username)
        if updated_context:
            print("✅ Contexto atualizado com sucesso")
            print(f"   Mundo: {updated_context.world_name}")
            print(f"   Tipo: {updated_context.world_type}")
            print(f"   Localizações: {len([e for e in updated_context.key_events if e.get('type') == 'location'])}")
        else:
            print("❌ Falha ao atualizar contexto")
            return False
        
        # Testar resumo de contexto
        print("\n📋 Testando resumo de contexto...")
        summary = context_manager.get_context_summary(test_channel_id)
        print("Resumo do contexto:")
        print(summary)
        
        # Testar análise de contexto com Gemini
        print("\n🤖 Testando análise de contexto com Gemini...")
        test_message2 = "Meu personagem é um guerreiro anão chamado Thorin que está em uma quest para encontrar o tesouro perdido"
        updated_context2 = context_manager.update_context(test_channel_id, test_message2, test_username)
        
        if updated_context2:
            print("✅ Análise de contexto funcionando")
            print(f"   Personagens: {len(updated_context2.player_characters)}")
            print(f"   Quests: {len([e for e in updated_context2.key_events if e.get('type') == 'quest'])}")
        else:
            print("❌ Falha na análise de contexto")
            return False
        
        print("\n✅ Todos os testes passaram!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_models():
    """Testa os modelos de dados"""
    print("\n🔧 Testando modelos de dados...")
    
    try:
        from rpg_tools.context_manager import RpgContext
        
        # Criar contexto de teste
        context = RpgContext(
            session_id="test_session",
            channel_id="test_channel",
            channel_name="test_channel"
        )
        
        # Testar serialização
        context_json = context.model_dump_json()
        print("✅ Serialização JSON funcionando")
        
        # Testar deserialização
        context_dict = context.model_dump()
        print("✅ Serialização para dict funcionando")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de contexto...")
    
    # Testar modelos
    models_ok = test_context_models()
    
    # Testar sistema completo
    if models_ok:
        system_ok = asyncio.run(test_context_system())
        success = system_ok
    else:
        success = False
    
    print(f"\n{'✅ Sistema funcionando!' if success else '❌ Sistema com problemas!'}")
    
    if not success:
        print("\n💡 Dicas para resolver problemas:")
        print("1. Verifique se Redis está rodando: redis-cli ping")
        print("2. Configure REDIS_URL no .env se necessário")
        print("3. Instale as dependências: pip install -r requirements.txt")
        print("4. Verifique se GOOGLE_API_KEY está configurada")
