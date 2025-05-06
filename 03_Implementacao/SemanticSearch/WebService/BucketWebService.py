import logging
import os
from urllib.parse import unquote
from pathlib import Path

from flask import Flask, request, jsonify, send_file, Response
from WebService.Controller.QueryController import QueryController
from WebService.Controller.StartUpController import StartUpController
from Manager.EmbeddingManager import EmbeddingManager


logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

class BucketWebService:
    def __init__(self):
        logger.debug("Initializing BucketWebService")
        self.embedding_manager = EmbeddingManager()
        self.startup_controller = StartUpController(self.embedding_manager)
        self.query_controller = QueryController(self.embedding_manager)

bucket_service = BucketWebService()

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

@app.route("/api")
def api_info():
    logger.info("Received request to API info endpoint")
    return jsonify({
        "message": "Welcome to the Semantic Search API!",
        "endpoints": {
            "startup": "GET /startup - Process documents from all subfolders in ./documents",
            "query": "POST /query - Query with JSON body (e.g., {'query': 'sample query', 'k': 3})",
            "download": "GET /download/<filename> - Download a specific .txt file"
        }
    })

@app.route("/startup", methods=["GET"])
def startup():
    logger.info("Received startup request")
    try:
        result = bucket_service.startup_controller.startup()
        logger.info(f"Startup response: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        return jsonify({"error": f"Startup failed: {str(e)}"}), 500

@app.route("/query", methods=["POST"])
def query():
    logger.info("Received query request")
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
        result = bucket_service.query_controller.handle_query(query_text, k)
        if not result["results"]:
            logger.warning("No documents found for query")
            return jsonify({"error": "No documents have been processed. Run /startup first."}), 400
        
        formatted_log = "\n".join(
            f"Name: {item['name']}, Similarity: {item['similarity']}, Location: {item['location']}"
            for item in result["results"]
        )
        logger.info(f"Query response:\n{formatted_log}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        return jsonify({"error": f"Query failed: {str(e)}"}), 500


@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    logger.info(f"Received download request for {filename}")
    # Decode URL-encoded filename
    filename = unquote(filename)
    
    # valida o do nome do arquivo
    if not filename.endswith(".txt"):
        logger.warning(f"Invalid file type for {filename}")
        return jsonify({"error": "Only .txt files can be downloaded"}), 400
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        logger.warning(f"Invalid filename: {filename}")
        return jsonify({"error": "Invalid filename"}), 400
    
    # caminho absoluto para o diretório de documentos
    base_dir = Path("./documents").resolve()
    logger.debug(f"Base directory resolved to: {base_dir}")
    
    # extração do nome do arquivo
    filename_base = os.path.basename(filename)
    logger.debug(f"Searching for filename: {filename_base}")
    
    # procura os documentos em ./documents and its subfolders
    file_path = None
    for root, _, files in os.walk(base_dir):
        if filename_base in files:
            file_path = Path(root) / filename_base
            logger.debug(f"Found file at: {file_path}")
            break
    
    # tambem tenta o caminho relativo (e.g., incident_reports/file.txt)
    if not file_path:
        relative_path = Path(filename).as_posix()  # normaliza o caminho
        full_path = base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            file_path = full_path
            logger.debug(f"Found file at relative path: {file_path}")
    
    if not file_path or not file_path.exists():
        logger.warning(f"File {filename_base} not found in {base_dir} or its subfolders")
        return jsonify({"error": f"File {filename_base} not found. Ensure the file exists and /startup has been run."}), 404
    
    try:
        logger.info(f"Sending file: {file_path}")
        return send_file(str(file_path), as_attachment=True, download_name=filename_base)
    except Exception as e:
        logger.error(f"Download failed for {filename}: {str(e)}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@app.route("/favicon.ico")
def favicon():
    return "", 204