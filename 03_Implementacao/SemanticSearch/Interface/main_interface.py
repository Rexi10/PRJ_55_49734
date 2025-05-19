import logging
import os
import asyncio
import requests
from flask import Flask, request, jsonify, Response, send_file, send_from_directory, redirect
from InterfaceWebService import InterfaceWebService


logger = logging.getLogger(__name__)

app = Flask(__name__)

interface_service = InterfaceWebService()

@app.route("/")
def index():
    logger.info("Serving React frontend")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
    except FileNotFoundError:
        logger.error("index.html not found in templates folder")
        return jsonify({"error": "Template not found"}), 500
    except Exception as e:
        logger.error(f"Failed to serve index.html: {str(e)}")
        return jsonify({"error": f"Failed to serve template: {str(e)}"}), 500

@app.route("/buckets", methods=["GET"])
def get_buckets():
    buckets = interface_service.ai_node.get_buckets()
    all_ready = all(b.get('status', 'ready') == 'ready' for b in buckets)
    return jsonify({"buckets": buckets, "all_ready": all_ready})

@app.route("/query", methods=["POST"])
def query():
    logger.info("Received query request")
    data = request.get_json()
    if not data or "query" not in data:
        logger.warning("Missing 'query' in request body")
        return jsonify({"error": "Query must be a non-empty string in the 'query' field", "results": []}), 400
    query_text = data.get("query", "")
    k = int(data.get("k", 3))
    selected_buckets = data.get("buckets", None)
    if not query_text:
        logger.warning("Empty query received")
        return jsonify({"error": "Query must be a non-empty string in the 'query' field", "results": []}), 400
    if k < 1:
        logger.warning("Invalid k value")
        return jsonify({"error": "k must be a positive integer", "results": []}), 400
    try:
        results = asyncio.run(interface_service.ai_node.forward_query(query_text, k, selected_buckets))
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

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # Try to find which bucket has the file and redirect
    for bucket in interface_service.ai_node.get_buckets():
        # Assuming files are not stored locally, but on the bucket's server
        # Redirect to the bucket's download endpoint
        return redirect(f"{bucket['url']}/download/{filename}")
    return jsonify({'error': 'File not found'}), 404

@app.route('/download/<bucket>/<path:filename>', methods=['GET'])
def proxy_download(bucket, filename):
    buckets = interface_service.ai_node.get_buckets()
    bucket_info = next((b for b in buckets if b['name'] == bucket), None)
    if not bucket_info:
        return jsonify({'error': 'Bucket not found'}), 404
    bucket_url = bucket_info['url']
    download_url = f"{bucket_url}/download/{filename}"
    try:
        r = requests.get(download_url, stream=True)
        if r.status_code != 200:
            return jsonify({'error': 'File not found in bucket'}), 404
        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                "Content-Disposition": f"attachment; filename={filename.split('/')[-1]}"
            },
            content_type=r.headers.get('Content-Type', 'application/octet-stream')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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