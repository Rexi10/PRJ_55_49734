import numpy as np
import logging
import json
import time
import os
import faiss
import ollama
from typing import List, Dict, Tuple
from SemanticSearch.Bucket.DAO import FileManagerDAO
from SemanticSearch.Bucket.Embeddings import Embedder, EmbeddingRepo

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuração
PORTUGUESE_DIR = "SemanticSearch/Bucket/buckets/bucket4/incident_reports_pt"
ENGLISH_DIR = "SemanticSearch/Bucket/buckets/bucket1/incident_reports"
K_VALUES = [3]
CHUNK_SIZES = [200, 300, 500]
OVERLAP_FRACTION = 0.5
RELEVANCE_THRESHOLD = 0.7
MODEL_NAME = "nomic_embed-text-v1.5"
MODEL_KEY = "teste"
# Consultas
PORTUGUESE_QUERIES = [
    "Quais são os relatórios recentes sobre atividades de gangues armadas em Vilkor, Zakovia?",
    "Quais são os relatórios mais recentes sobre roubos de arte envolvendo os Ghost Shadows em Ravenska, Zakovia?",
    "Quais incidentes envolvendo os esquemas de proteção dos Blood Ravens ocorreram perto de Baron’s Peak em 2023?",
    "Quais são os casos de contrabando de armas relatados em Sokovia em 2024?",
    "Quais atividades criminosas dos Night Vipers foram documentadas em Krov, Zakovia?",
    "Quais são as políticas de turismo sustentável em Ravenska, Zakovia?"
]

NOISY_PORTUGUESE_QUERIES = [
    "Quais são os relatórrios resentes sobbre atividdades de ganguues armadaz em Vilkorr, Zakovia?",
    "Quais são os relatórios mais recntes sobre rouboos de arte enolvendo os Ghoost Shadws em Ravennska, Zakovia?",
    "Quais incidntes envovendo os esquemmas de proteçção dos Blod Ravns ocoreram perto de Baroon’s Peek em 2023?",
    "Quais são os casso de contrabbando de armaz relatadoz em Sokovia em 2024?",
    "Quais atvidades criminossas dos Nigt Viipers foram documntadas em Kroov, Zakovia?",
    "Quais são as políicas de turismmo sustntável em Ravennska, Zakovia?"
]

ENGLISH_QUERIES = [
    "What are the recent reports on armed gang activities in Vilkor, Zakovia?",
    "What are the latest reports on art thefts involving the Ghost Shadows in Ravenska, Zakovia?",
    "Which incidents involving the Blood Ravens' protection rackets occurred near Baron’s Peak in 2023?",
    "What are the reported cases of arms smuggling in Sokovia in 2024?",
    "What criminal activities by the Night Vipers were documented in Krov, Zakovia?",
    "What are the sustainable tourism policies in Ravenska, Zakovia?"
]

NOISY_ENGLISH_QUERIES = [
    "Wht are the recnt reportts on armd gang activties in Vilkor, Zakoviia?",
    "What are the latst reports on art thefths involvng the Ghosst Shdows in Ravennska, Zakovia?",
    "Which inciddents invlving the Bloood Ravns' protecton rackets occurrd near Baronn’s Peak in 2023?",
    "What are the reportd casess of arms smugling in Sokovvia in 2024?",
    "What crimnal activties by the Niight Vipers were docummented in Kroov, Zakovia?",
    "What are the sustanable tourissm policiies in Ravennska, Zakovia?"
]

class Doc:
    def __init__(self, name: str, location: str, content: str):
        self.name = name
        self.location = location
        self.content = content
        self.embeddings = []
        self.metadata = {}

def parse_text_file(file_path: str) -> Dict[str, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.debug(f"Analisado com sucesso {file_path}")
        return {"content": content}
    except Exception as e:
        logger.error(f"Falha ao analisar {file_path}: {str(e)}")
        return {"content": None, "error": str(e)}

def process_documents(directory: str, model: str, chunk_size: int) -> Tuple[EmbeddingRepo, float, float, List[int]]:
    if not os.path.exists(directory):
        logger.error(f"Diretório {directory} não existe")
        return EmbeddingRepo(), 0.0, 0.0, []

    overlap_words = int(chunk_size * OVERLAP_FRACTION)
    start_time = time.time()
    file_manager = FileManagerDAO(directory)
    embedding_repo = EmbeddingRepo()
    embedder = Embedder(model)
    total_embedding_time = 0.0
    chunk_counts = []

    docs = file_manager.get_docs()
    logger.info(f"Encontrados {len(docs)} ficheiros em {directory}")
    txt_count = 0
    for doc_info in docs:
        if not doc_info["name"].lower().endswith(".txt"):
            logger.debug(f"A ignorar ficheiro não-.txt: {doc_info['name']}")
            continue
        file_path = os.path.join(directory, doc_info["location"])
        if not os.path.exists(file_path):
            logger.error(f"Ficheiro não encontrado: {file_path}")
            continue
        result = parse_text_file(file_path)
        if result.get("content") is None:
            logger.error(f"Falha ao analisar {file_path}: {result.get('error', 'Erro desconhecido')}")
            continue
        content = result["content"]
        doc = Doc(name=doc_info["name"], location=file_path, content=content)
        try:
            chunks = embedder.chunk_content(content, chunk_size, overlap_words)
            chunk_counts.append(len(chunks))
            doc.embeddings = []
            for chunk in chunks:
                embedding, emb_time = embedder.generate_embedding(chunk)
                doc.embeddings.append(embedding)
                total_embedding_time += emb_time
            embedding_repo.save(doc, chunks)
            logger.info(f"Processado {doc_info['name']} com {len(chunks)} chunks (chunk_size={chunk_size})")
            txt_count += 1
        except Exception as e:
            logger.error(f"Falha ao incorporar {file_path}: {str(e)}")

    processing_time = time.time() - start_time
    logger.info(f"Modelo {model} processou {txt_count} documentos .txt com chunk_size={chunk_size} em {processing_time:.4f}s, tempo total de embedding={total_embedding_time:.4f}s, tamanho do índice FAISS={embedding_repo.faiss_index.ntotal}")
    return embedding_repo, processing_time, total_embedding_time, chunk_counts

def query_search(query: str, model: str, k: int, embedding_repo: EmbeddingRepo) -> Tuple[List[float], float, float, List[str]]:
    start_time = time.time()
    embedder = Embedder(model)
    try:
        query_embedding, emb_time = embedder.generate_embedding(query)
        results = embedding_repo.search(query_embedding, k)
        similarities = [float(similarity) for doc, similarity, _, _ in results]
        doc_names = [doc.name for doc, _, _, _ in results]
        query_time = time.time() - start_time
        logger.info(f"Consulta '{query}' com modelo {model}, K={k}: similaridades={similarities}, documentos recuperados={doc_names}, tempo={query_time:.4f}s, emb_time={emb_time:.4f}s")
        return similarities, query_time, emb_time, doc_names
    except Exception as e:
        logger.error(f"Consulta falhou para modelo {model}: {str(e)}")
        return [], 0.0, 0.0, []

def evaluate_model(model: str, queries: list, k_values: List[int], embedding_repo: EmbeddingRepo, query_type: str) -> Dict[int, Tuple[float, float, float, float]]:
    results = {}
    for k in k_values:
        all_similarities = []
        query_times = []
        embedding_times = []
        relevant_counts = []
        try:
            for query in queries:
                similarities, query_time, emb_time, _ = query_search(query, model, k, embedding_repo)
                all_similarities.extend(similarities)
                query_times.append(query_time)
                embedding_times.append(emb_time)
                relevant_counts.append(sum(1 for sim in similarities if sim >= RELEVANCE_THRESHOLD))
            avg_similarity = np.mean(all_similarities) if all_similarities else 0.0
            avg_query_time = np.mean(query_times) if query_times else 0.0
            avg_embedding_time = np.mean(embedding_times) if embedding_times else 0.0
            precision_at_k = np.mean([count / k for count in relevant_counts]) if relevant_counts else 0.0
            logger.info(f"Modelo {model} processou {len(queries)} consultas {query_type}, K={k}: similaridade média={avg_similarity:.4f}, tempo médio de consulta={avg_query_time:.4f}s, tempo médio de emb={avg_embedding_time:.4f}s, Precisão@K={precision_at_k:.4f}")
            results[k] = (avg_similarity, avg_query_time, avg_embedding_time, precision_at_k)
        except Exception as e:
            logger.error(f"Avaliação falhou para modelo {model}, K={k}, tipo de consulta={query_type}: {str(e)}")
            results[k] = (0.0, 0.0, 0.0, 0.0)
    return results

def main():
    total_start_time = time.time()
    results = {"portuguese": {}, "english": {}}

    pt_has_docs = os.path.exists(PORTUGUESE_DIR)
    en_has_docs = os.path.exists(ENGLISH_DIR)
    if not (pt_has_docs or en_has_docs):
        logger.error("Nem o diretório Português nem o Inglês existem. A terminar.")
        return

    for chunk_size in CHUNK_SIZES:
        pt_results = {MODEL_KEY: {}}
        en_results = {MODEL_KEY: {}}

        if pt_has_docs:
            try:
                repo, doc_time, emb_time, chunks = process_documents(PORTUGUESE_DIR, MODEL_NAME, chunk_size)
                pt_results[MODEL_KEY]["doc_processing_time"] = doc_time
                pt_results[MODEL_KEY]["total_embedding_time"] = emb_time
                pt_results[MODEL_KEY]["avg_chunk_count"] = np.mean(chunks) if chunks else 0.0
                if repo.faiss_index.ntotal > 0:
                    k_results = evaluate_model(MODEL_NAME, PORTUGUESE_QUERIES, K_VALUES, repo, "standard")
                    for k, (sim, q_time, e_time, prec) in k_results.items():
                        pt_results[MODEL_KEY][f"K{k}_similarity"] = sim
                        pt_results[MODEL_KEY][f"K{k}_query_time"] = q_time
                        pt_results[MODEL_KEY][f"K{k}_embedding_time"] = e_time
                        pt_results[MODEL_KEY][f"K{k}_precision"] = prec
                    k_results_noisy = evaluate_model(MODEL_NAME, NOISY_PORTUGUESE_QUERIES, K_VALUES, repo, "noisy")
                    for k, (sim, _, _, _) in k_results_noisy.items():
                        pt_results[MODEL_KEY][f"K{k}_noisy_similarity"] = sim
            except Exception as e:
                logger.error(f"Falha ao processar documentos Portugueses para modelo {MODEL_NAME}, chunk_size={chunk_size}: {str(e)}")
                pt_results[MODEL_KEY]["doc_processing_time"] = 0.0
                pt_results[MODEL_KEY]["total_embedding_time"] = 0.0
                pt_results[MODEL_KEY]["avg_chunk_count"] = 0.0
                for k in K_VALUES:
                    pt_results[MODEL_KEY][f"K{k}_similarity"] = 0.0
                    pt_results[MODEL_KEY][f"K{k}_query_time"] = 0.0
                    pt_results[MODEL_KEY][f"K{k}_embedding_time"] = 0.0
                    pt_results[MODEL_KEY][f"K{k}_precision"] = 0.0
                    pt_results[MODEL_KEY][f"K{k}_noisy_similarity"] = 0.0

        if en_has_docs:
            try:
                repo, doc_time, emb_time, chunks = process_documents(ENGLISH_DIR, MODEL_NAME, chunk_size)
                en_results[MODEL_KEY]["doc_processing_time"] = doc_time
                en_results[MODEL_KEY]["total_embedding_time"] = emb_time
                en_results[MODEL_KEY]["avg_chunk_count"] = np.mean(chunks) if chunks else 0.0
                if repo.faiss_index.ntotal > 0:
                    k_results = evaluate_model(MODEL_NAME, ENGLISH_QUERIES, K_VALUES, repo, "standard")
                    for k, (sim, q_time, e_time, prec) in k_results.items():
                        en_results[MODEL_KEY][f"K{k}_similarity"] = sim
                        en_results[MODEL_KEY][f"K{k}_query_time"] = q_time
                        en_results[MODEL_KEY][f"K{k}_embedding_time"] = e_time
                        en_results[MODEL_KEY][f"K{k}_precision"] = prec
                    k_results_noisy = evaluate_model(MODEL_NAME, NOISY_ENGLISH_QUERIES, K_VALUES, repo, "noisy")
                    for k, (sim, _, _, _) in k_results_noisy.items():
                        en_results[MODEL_KEY][f"K{k}_noisy_similarity"] = sim
            except Exception as e:
                logger.error(f"Falha ao processar documentos Ingleses para modelo {MODEL_NAME}, chunk_size={chunk_size}: {str(e)}")
                en_results[MODEL_KEY]["doc_processing_time"] = 0.0
                en_results[MODEL_KEY]["total_embedding_time"] = 0.0
                en_results[MODEL_KEY]["avg_chunk_count"] = 0.0
                for k in K_VALUES:
                    en_results[MODEL_KEY][f"K{k}_similarity"] = 0.0
                    en_results[MODEL_KEY][f"K{k}_query_time"] = 0.0
                    en_results[MODEL_KEY][f"K{k}_embedding_time"] = 0.0
                    en_results[MODEL_KEY][f"K{k}_precision"] = 0.0
                    en_results[MODEL_KEY][f"K{k}_noisy_similarity"] = 0.0

        results["portuguese"][f"chunk_size_{chunk_size}"] = pt_results
        results["english"][f"chunk_size_{chunk_size}"] = en_results

        # Guarda num ficheiro específico do modelo
        results_file = f"results_{MODEL_KEY}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Resultados guardados para modelo {MODEL_NAME}, chunk_size={chunk_size} em {results_file}")

    total_time = time.time() - total_start_time
    logger.info(f"Tempo total de execução para modelo {MODEL_NAME}: {total_time:.4f} segundos")

if __name__ == "__main__":
    main()