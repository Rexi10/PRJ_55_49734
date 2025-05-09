import logging
import os
import asyncio
from flask import Flask, request, jsonify, Response
from InterfaceWebService import InterfaceWebService


logger = logging.getLogger(__name__)

app = Flask(__name__)

interface_service = InterfaceWebService()

@app.route("/")
def index():
    logger.info("Serving React frontend")
    try:
        with open(os.path.join("templates", "index.html"), "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
    except FileNotFoundError:
        logger.error("index.html not found in templates folder")
        return jsonify({"error": "Template not found"}), 500
    except Exception as e:
        logger.error(f"Failed to serve index.html: {str(e)}")
        return jsonify({"error": f"Failed to serve template: {str(e)}"}), 500

@app.route("/buckets", methods=["GET"])
def get_buckets():
    logger.info("Received request for bucket list")
    buckets = interface_service.ai_node.get_buckets()
    return jsonify({"buckets": buckets})

@app.route("/query", methods=["POST"])
def query():
    logger.info("Received query request")
    data = request.get_json()
    if not data or "query" not in data:
        logger.warning("Missing 'query' in request body")
        return jsonify({"error": "Query must be a non-empty string in the 'query' field", "results": []}), 400
    query_text = data.get("query", "")
    k = int(data.get("k", 3))
    if not query_text:
        logger.warning("Empty query received")
        return jsonify({"error": "Query must be a non-empty string in the 'query' field", "results": []}), 400
    if k < 1:
        logger.warning("Invalid k value")
        return jsonify({"error": "k must be a positive integer", "results": []}), 400
    try:
        results = asyncio.run(interface_service.ai_node.forward_query(query_text, k))
        if not isinstance(results, dict):
            logger.error(f"Invalid results type from forward_query: {type(results)}, value: {results}")
            return jsonify({"error": "Invalid response from buckets", "results": []}), 500
        flat_results = []
        for bucket_name, bucket_results in results.items():
            if not isinstance(bucket_results, list):
                logger.warning(f"Invalid results from {bucket_name}: {bucket_results}")
                continue
            for result in bucket_results:
                result['bucket_name'] = bucket_name
                flat_results.append(result)
        if not flat_results:
            logger.info("No results from any bucket")
            return jsonify({"results": []}), 200
        logger.info(f"Query returned results from {len([r for r in results.values() if r])} buckets")
        return jsonify({"results": flat_results})
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        return jsonify({"error": f"Query failed: {str(e)}", "results": []}), 500

@app.route("/ai-node/register", methods=["POST"])
def register_bucket():
    logger.info("Received bucket registration request")
    data = request.get_json()
    if not data or "name" not in data or "url" not in data:
        logger.warning("Missing 'name' or 'url' in request body")
        return jsonify({"error": "Must provide 'name' and 'url'"}), 400
    bucket_name = data["name"]
    bucket_url = data["url"]
    if not bucket_name or not bucket_url:
        logger.warning("Empty bucket name or URL")
        return jsonify({"error": "Bucket name and URL must be non-empty"}), 400
    try:
        success = interface_service.ai_node.register_bucket(bucket_name, bucket_url)
        if success:
            logger.info(f"Bucket {bucket_name} registered successfully")
            return jsonify({"message": f"Bucket {bucket_name} registered at {bucket_url}"})
        else:
            logger.error(f"Failed to register bucket {bucket_name}")
            return jsonify({"error": f"Failed to register bucket {bucket_name}"}), 500
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@app.route("/startup", methods=["GET"])
def startup():
    logger.info("Received startup check request")
    return jsonify({"message": "Processed"})


@app.route("/favicon.ico")
def favicon():
    return "", 204

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('interface.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

if __name__ == "__main__":
    logger.info("Starting InterfaceWebService initialization")
    interface_service = InterfaceWebService()
    logger.info("InterfaceWebService initialized, starting Flask app")
    app.run(host="0.0.0.0", port=5000, debug=False)