import os
import google.generativeai as genai
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import pickle
import re
from typing import List, Dict, Any
import logging
from en_terms import dnd_dictionary_pt_en
from discord_tools.chat import Chat

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DNDRagSystem:
    """Sistema RAG para consultar regras de D&D usando Gemini - Integrado com Discord"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o sistema RAG
        
        Args:
            api_key: Chave da API do Google Gemini
        """
        # Configurar API do Gemini
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Tentar carregar da variável de ambiente
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada. Configure a variável de ambiente ou passe como parâmetro.")
            genai.configure(api_key=api_key)
        
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Inicializar modelo de embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Configurar text splitter (chunks menores para economizar tokens)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Variáveis para armazenar dados
        self.chunks = []
        self.embeddings = None
        self.index = None
        
    def load_and_process_document(self, file_path: str) -> None:
        """
        Carrega e processa o documento D&D
        
        Args:
            file_path: Caminho para o arquivo dnd.txt
        """
        logger.info("Carregando documento D&D...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # Tentar com encoding latin-1 se UTF-8 falhar
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        
        logger.info(f"Documento carregado. Tamanho: {len(content)} caracteres")
        
        # Limpar e preprocessar o texto
        content = self._clean_text(content)
        
        # Dividir em chunks
        logger.info("Dividindo documento em chunks...")
        self.chunks = self.text_splitter.split_text(content)
        logger.info(f"Documento dividido em {len(self.chunks)} chunks")
        
        # Criar embeddings
        self._create_embeddings()
        
        # Criar índice FAISS
        self._create_faiss_index()
        
    def _clean_text(self, text: str) -> str:
        """
        Limpa e preprocessa o texto
        
        Args:
            text: Texto bruto
            
        Returns:
            Texto limpo
        """
        # Remover caracteres especiais desnecessários
        text = re.sub(r'\s+', ' ', text)  # Múltiplos espaços em branco
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Múltiplas quebras de linha
        text = text.strip()
        
        return text
    
    def _create_embeddings(self) -> None:
        """Cria embeddings para todos os chunks"""
        logger.info("Criando embeddings...")
        
        # Gerar embeddings em lotes para eficiência
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i+batch_size]
            batch_embeddings = self.embedding_model.encode(batch, convert_to_numpy=True)
            all_embeddings.append(batch_embeddings)
        
        self.embeddings = np.vstack(all_embeddings)
        logger.info(f"Embeddings criados. Shape: {self.embeddings.shape}")
    
    def _create_faiss_index(self) -> None:
        """Cria índice FAISS para busca vetorial"""
        logger.info("Criando índice FAISS...")
        
        # Normalizar embeddings para usar cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        # Criar índice
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        self.index.add(self.embeddings)
        
        logger.info(f"Índice FAISS criado com {self.index.ntotal} vetores")
    
    def search_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca chunks relevantes para a consulta
        
        Args:
            query: Consulta do usuário
            top_k: Número de chunks mais relevantes para retornar
            
        Returns:
            Lista de chunks relevantes com scores
        """
        if self.index is None:
            raise ValueError("Índice não foi criado. Execute load_and_process_document primeiro.")
        
        # Criar embedding da consulta
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Buscar chunks similares
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            results.append({
                'chunk': self.chunks[idx],
                'score': float(score),
                'index': int(idx),
                'rank': i + 1
            })
        
        return results
    
    def generate_answer(self, chat: Chat, query: str, top_k: int = 3) -> str:
        """
        Gera resposta usando RAG com Gemini - Otimizado para Discord
        
        Args:
            query: Pergunta do usuário
            top_k: Número de chunks para usar como contexto
            
        Returns:
            Resposta gerada
        """
        # Buscar chunks relevantes (tentar português e inglês)
        relevant_chunks = self.search_relevant_chunks(query, top_k)
        
        # Se não encontrou bons resultados, tentar traduzir termos chave
        if len(relevant_chunks) == 0 or relevant_chunks[0]['score'] < 0.3:
            # Traduzir termos usando o dicionário extenso
            english_query = query.lower()
            for pt, en in dnd_dictionary_pt_en.items():
                english_query = english_query.replace(pt, en)
            
            if english_query != query.lower():
                english_chunks = self.search_relevant_chunks(english_query, top_k)
                if len(english_chunks) > 0 and english_chunks[0]['score'] > relevant_chunks[0]['score']:
                    relevant_chunks = english_chunks
        
        # Construir contexto
        context = "\n\n".join([f"[Regra {result['rank']} score {result['score']}]: {result['chunk']}" 
                              for result in relevant_chunks])
        
        # Prompt otimizado para Discord
        prompt = f"""{chat.preinitialization}

INSTRUÇÕES IMPORTANTES:

- SEMPRE use as regras fornecidas acima para responder
- Responda em português brasileiro
- Seja direto e útil para Discord
- Se há informação relevante nas regras, USE-A na resposta
- Organize as informações de forma clara

RESPOSTA baseado nas regras fornecidas:

REGRAS D&D FORNECIDAS:
{context}

Agora iniciam as mensagens:
{chat.chat_text}{chat.postinitialization()} """
        # print("Prompt:" , prompt)
        try:
            # Gerar resposta com Gemini
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return f"❌ Erro ao consultar regras D&D: {str(e)}"
    
    def is_dnd_question(self, query: str) -> bool:
        """
        Verifica se a pergunta é relacionada a D&D
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            True se for pergunta sobre D&D
        """
        query_lower = query.lower()
        
        # Verificar se alguma palavra da query está nas chaves (português) do dicionário
        for pt_term in dnd_dictionary_pt_en.keys():
            if pt_term in query_lower:
                return True
        
        # Verificar se alguma palavra da query está nos valores (inglês) do dicionário
        for en_term in dnd_dictionary_pt_en.values():
            if en_term in query_lower:
                return True
        
        return False
    
    def save_index(self, index_path: str = "dnd_index.pkl") -> None:
        """Salva o índice e dados para reuso futuro"""
        data = {
            'chunks': self.chunks,
            'embeddings': self.embeddings
        }
        
        with open(index_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Salvar índice FAISS separadamente
        faiss.write_index(self.index, index_path.replace('.pkl', '.faiss'))
        logger.info(f"Índice salvo em {index_path}")
    
    def load_index(self, index_path: str = "dnd_index.pkl") -> None:
        """Carrega índice previamente salvo"""
        with open(index_path, 'rb') as f:
            data = pickle.load(f)
        
        self.chunks = data['chunks']
        self.embeddings = data['embeddings']
        
        # Carregar índice FAISS
        self.index = faiss.read_index(index_path.replace('.pkl', '.faiss'))
        logger.info(f"Índice carregado de {index_path}")


def initialize_rag_system():
    """
    Inicializa o sistema RAG para uso global
    
    Returns:
        DNDRagSystem inicializado
    """
    print("🎲 Inicializando Sistema RAG D&D para Discord...")
    
    # Verificar se o arquivo D&D existe
    dnd_file = "dnd.txt"
    if not os.path.exists(dnd_file):
        print(f"❌ Arquivo {dnd_file} não encontrado!")
        return None
    
    try:
        # Inicializar sistema RAG
        rag_system = DNDRagSystem()
        
        # Verificar se índice já existe
        if os.path.exists("dnd_index.pkl") and os.path.exists("dnd_index.faiss"):
            print("📚 Carregando índice existente...")
            rag_system.load_index()
        else:
            print("📚 Processando documento D&D (pode demorar alguns minutos)...")
            rag_system.load_and_process_document(dnd_file)
            print("💾 Salvando índice para uso futuro...")
            rag_system.save_index()
        
        print("✅ Sistema RAG D&D inicializado com sucesso!")
        return rag_system
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema RAG: {e}")
        logger.error(f"Erro detalhado: {e}", exc_info=True)
        return None


# Instância global do sistema RAG
global_rag_system = None

def get_rag_system():
    """Retorna a instância global do sistema RAG"""
    global global_rag_system
    if global_rag_system is None:
        global_rag_system = initialize_rag_system()
    return global_rag_system


if __name__ == "__main__":
    # Teste do sistema RAG
    rag = initialize_rag_system()
    if rag:
        chat = Chat()
        chat.SetName("LLM", False)
        test_query = "Quais são as características dos Anões?"
        print(f"\n🧪 Teste: {test_query}")
        chat.chat_text += f"$ Mensagem de Fulaninho: {test_query}\n\n"
        response = rag.generate_answer(chat, test_query)
        print(f"📝 Resposta: {response}")
