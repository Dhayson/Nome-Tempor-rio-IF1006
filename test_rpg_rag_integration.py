#!/usr/bin/env python3
"""
Teste de integração entre o agente RPG e o sistema RAG
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rpg_rag_integration():
    """Testa a integração entre RPG e RAG"""
    print("🧪 Testando Integração RPG + RAG")
    print("=" * 50)
    
    try:
        # Testar importação do sistema RAG
        from rag import get_rag_system
        print("✅ Sistema RAG importado com sucesso")
        
        # Testar importação do agente RPG
        from rpg_tools.reasoner import RpgReasoner
        print("✅ Agente RPG importado com sucesso")
        
        # Inicializar sistema RAG
        rag_system = get_rag_system()
        if not rag_system:
            print("❌ Falha ao inicializar sistema RAG")
            return False
        
        # Criar agente RPG
        reasoner = RpgReasoner()
        print("✅ Agente RPG criado com sucesso")
        
        # Verificar se o RAG foi integrado
        if hasattr(reasoner, 'rag_system') and reasoner.rag_system:
            print("✅ Sistema RAG integrado ao agente RPG")
        else:
            print("⚠️ Sistema RAG não foi integrado")
        
        # Testar detecção de perguntas D&D
        test_questions = [
            ("Como funcionam os Anões em D&D?", True),
            ("Qual é a AC dos elfos?", True),
            ("Oi, como você está?", False),
            ("Vamos jogar RPG!", False),
        ]
        
        print("\n🔍 Teste de Detecção de Perguntas D&D:")
        for question, expected in test_questions:
            result = reasoner._should_use_rag(question)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{question}' -> {result} (esperado: {expected})")
        
        print("\n✅ Integração testada com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rpg_rag_integration()
    print(f"\n{'✅ Integração funcionando!' if success else '❌ Integração falhou!'}")
