import logging
import time
from flask import request, jsonify
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class QueryController:
    # Inicializa com gestor de embeddings
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def register_routes(self, app):
        @app.route("/query", methods=["POST"])
        def query_endpoint():
            query_start = time.time()
            logger.info("Recebido pedido de consulta")

            # Verifica se o sistema está pronto
            if not getattr(app, "processing_complete", False):
                return jsonify({"error": "O bucket ainda está a carregar e não está pronto para consultas."}), 503

            data = request.get_json()
            if not data or "query" not in data:
                return jsonify({"error": "A consulta deve ser uma string não vazia no campo 'query'"}), 400
            
            query_text = data.get("query", "")
            k = int(data.get("k", 3))
            
            # Valida consulta não vazia
            if not query_text:
                return jsonify({"error": "A consulta deve ser uma string não vazia no campo 'query'"}), 400
            
            if k < 1:
                return jsonify({"error": "k deve ser um inteiro positivo"}), 400
            
            try:
                logger.debug(f"Processando consulta: {query_text} com k={k}")
                result = self.embedding_manager.process_query(query_text, k)
                logger.debug(f"Resultado da consulta: {result}")
                
                # Calcula tempo de processamento
                query_time = time.time() - query_start
                logger.info(f"Consulta processada em {query_time:.4f} segundos")
                
                if not result["results"]:
                    return jsonify({"error": "Nenhum documento foi processado. Execute /bucket-startup primeiro."}), 400
                
                enhanced_results = []
                for item in result["results"]:
                    logger.debug(f"A processar item de resultado: {item}")
                    doc = next((d for d, _, _ in self.embedding_manager.embedding_repo.docs 
                                if d.name == item["name"] and d.location == item["location"]), None)
                    if not doc:
                        continue
                    
                    # Adiciona chunk do documento
                    chunk = item.get("chunk", doc.content if doc.content else "Sem chunk disponível")
                    enhanced_results.append({
                        "name": item["name"],
                        "location": item["location"],
                        "similarity": item["similarity"],
                        "chunk": chunk
                    })
                
                formatted_log = "\n".join(
                    f"Name: {item['name']}, Similarity: {item['similarity']}, Location: {item['location']}"
                    for item in result["results"]
                )
                logger.info(f"Resposta da consulta:\n{formatted_log}")
                
                # Retorna resultados com tempo
                return jsonify({
                    "results": result["results"],
                    "query_time": query_time
                })
            
            # Trata erros inesperados
            except Exception as e:
                logger.error(f"Falha na consulta: {str(e)}", exc_info=True)
                return jsonify({"error": f"Falha na consulta: {str(e)}"}), 500
