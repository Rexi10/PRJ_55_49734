import logging
import os
from urllib.parse import unquote
from pathlib import Path
from flask import Flask, request, jsonify, send_file, Response
from BucketWebService import BucketWebService

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')

bucket_service = BucketWebService()


@app.route("/api")
def api_info():
    logger.info("Received request to API info endpoint")
    return jsonify({
        "message": f"Welcome to {bucket_service.bucket_name} Semantic Search API!",
        "endpoints": {
            "startup": "GET /startup - Process documents from all subfolders in bucket folder",
            "query": "POST /query - Query with JSON body (e.g., {'query': 'sample query', 'k': 3})",
            "download": "GET /download/<filename> - Download a file"
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

        
@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    logger.info(f"Received download request for {filename}")
    filename = unquote(filename)
    
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        logger.warning(f"Invalid filename: {filename}")
        return jsonify({"error": "Invalid filename"}), 400
    
    base_dir = Path(bucket_service.bucket_folder).resolve()
    logger.debug(f"Base directory resolved to: {base_dir}")
    
    filename_base = os.path.basename(filename)
    logger.debug(f"Searching for filename: {filename_base}")
    
    file_path = None
    for root, _, files in os.walk(base_dir):
        if filename_base in files:
            file_path = Path(root) / filename_base
            logger.debug(f"Found file at: {file_path}")
            break
    
    if not file_path:
        relative_path = Path(filename).as_posix()
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('bucket.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

@app.route('/')
def index():
    return jsonify({
        'message': 'Bucket Web Service',
        'bucket_name': os.getenv('BUCKET_NAME', 'default_bucket'),
        'bucket_folder': os.getenv('BUCKET_FOLDER', './documents')
    })

if __name__ == "__main__":
    logger.info("Starting BucketWebService initialization")
    try:
        bucket_service = BucketWebService()
        logger.info("BucketWebService initialized, setting up Flask app")
        bucket_service.set_app(app)
        logger.info("Starting Flask app")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {str(e)}")
        raise