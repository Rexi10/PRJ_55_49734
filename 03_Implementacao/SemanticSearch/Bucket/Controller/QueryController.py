import logging
import time
from flask import request, jsonify
from Manager import EmbeddingManager

logger = logging.getLogger(__name__)

class QueryController:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def register_routes(self, app):
        @app.route("/query", methods=["POST"])
        def query_endpoint():
            query_start = time.time()
            logger.info("Received query request")

            if not getattr(app, "processing_complete", False):
                logger.warning("Bucket is still loading and not ready for queries.")
                return jsonify({"error": "Bucket is still loading and not ready for queries."}), 503

            data = request.get_json()
            if not data or "query" not in data:
                logger.warning("Missing 'query' in request body")
                return jsonify({"error": "Query must be a non-empty string in the 'query' field"}), 400
            query_text = data.get("query", "")
            k = int(data.get("k", 3))
            if not query_text:
                logger.warning("Empty query received")
                return jsonify({"error": "Query must be a non-empty string in the 'query' field"}), 400
            if k < 1:
                logger.warning("Invalid k value")
                return jsonify({"error": "k must be a positive integer"}), 400
            try:
                logger.debug(f"Processing query: {query_text} with k={k}")
                result = self.embedding_manager.process_query(query_text, k)
                logger.debug(f"Query result: {result}")
                query_time = time.time() - query_start
                logger.info(f"Query processed in {query_time:.4f} seconds")
                if not result["results"]:
                    logger.warning("No documents found for query")
                    return jsonify({"error": "No documents have been processed. Run /bucket-startup first."}), 400
                
                enhanced_results = []
                for item in result["results"]:
                    logger.debug(f"Processing result item: {item}")
                    doc = next((d for d, _, _ in self.embedding_manager.embedding_repo.docs 
                                if d.name == item["name"] and d.location == item["location"]), None)
                    if not doc:
                        logger.warning(f"No document found for name={item['name']}, location={item['location']}")
                        continue
                    chunk = item.get("chunk", doc.content if doc.content else "No chunk available")
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
                logger.info(f"Query response:\n{formatted_log}")
                
                # Optionally include query time in response
                return jsonify({
                    "results": result["results"],
                    "query_time": query_time  # Add this line
                })
            except Exception as e:
                logger.error(f"Query failed: {str(e)}", exc_info=True)
                return jsonify({"error": f"Query failed: {str(e)}"}), 500