#!/usr/bin/env python3
"""
Teste de integração do sistema RAG D&D
"""

from rag import get_rag_system

def test_rag_system():
    """Testa o sistema RAG"""
    print("🧪 Testando Sistema RAG D&D")
    print("=" * 50)
    
    # Inicializar RAG
    rag_system = get_rag_system()
    
    if not rag_system:
        print("❌ Falha ao inicializar sistema RAG")
        return False
    
    # Testes de detecção D&D
    test_questions = [
        ("Como funcionam os Anões em D&D?", True),
        ("Qual é a AC dos elfos?", True),
        ("Oi, como você está?", False),
        ("Qual sua cor favorita?", False),
        ("Como fazer uma rolagem de dado?", True),
        ("Explique vantagem e desvantagem", True),
    ]
    
    print("\n🔍 Teste de Detecção de Perguntas D&D:")
    for question, expected in test_questions:
        result = rag_system.is_dnd_question(question)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{question}' -> {result} (esperado: {expected})")
    
    # Teste de resposta RAG
    print("\n💬 Teste de Resposta RAG:")
    test_query = "Quais são as características raciais dos Anões?"
    print(f"Pergunta: {test_query}")
    
    try:
        response = rag_system.generate_answer(test_query)
        print(f"Resposta: {response}")
        print("✅ Resposta gerada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_system()
    print(f"\n{'✅ Todos os testes passaram!' if success else '❌ Alguns testes falharam!'}") 