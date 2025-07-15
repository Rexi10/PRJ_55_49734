import logging
import os
import ollama
from urllib.parse import unquote
from pathlib import Path
from flask import Flask, request, jsonify, send_file, Response
from BucketWebService import BucketWebService

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
bucket_service = BucketWebService()

@app.route("/api")
def api_info():
    logger.info("Recebido pedido para endpoint de informação da API")
    return jsonify({
        "message": f"Bem-vindo à API de Pesquisa Semântica de {bucket_service.bucket_name}!",
        "endpoints": {
            "startup": "GET /startup - Processa documentos de todas as subpastas na pasta do bucket",
            "query": "POST /query - Consulta com corpo JSON (ex.: {'query': 'exemplo de consulta', 'k': 3})",
            "download": "GET /download/<filename> - Descarrega um arquivo"
        }
    })

@app.route("/startup", methods=["GET"])
def startup():
    logger.info("Recebido pedido de inicialização")
    try:
        result = bucket_service.startup_controller.startup()
        logger.info(f"Resposta de inicialização: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Inicialização falhou: {str(e)}")
        return jsonify({"error": f"Inicialização falhou: {str(e)}"}), 500

@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    logger.info(f"Recebido pedido de download para {filename}")
    filename = unquote(filename)
    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        logger.warning(f"Nome do arquivo inválido: {filename}")
        return jsonify({"error": "Nome do arquivo inválido"}), 400
    base_dir = Path(bucket_service.bucket_folder).resolve()
    logger.debug(f"Diretório base resolvido para: {base_dir}")
    filename_base = os.path.basename(filename)
    logger.debug(f"A procurar arquivo: {filename_base}")
    file_path = None
    for root, _, files in os.walk(base_dir):
        if filename_base in files:
            file_path = Path(root) / filename_base
            logger.debug(f"Arquivo encontrado em: {file_path}")
            break
    if not file_path:
        relative_path = Path(filename).as_posix()
        full_path = base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            file_path = full_path
            logger.debug(f"Arquivo encontrado no caminho relativo: {file_path}")
    if not file_path or not file_path.exists():
        logger.warning(f"Arquivo {filename_base} não encontrado em {base_dir} ou subpastas")
        return jsonify({"error": f"Arquivo {filename_base} não encontrado."}), 404
    try:
        logger.info(f"A enviar arquivo: {file_path}")
        return send_file(str(file_path), as_attachment=True, download_name=filename_base)
    except Exception as e:
        logger.error(f"Download falhou para {filename}: {str(e)}")
        return jsonify({"error": f"Download falhou: {str(e)}"}), 500

@app.route("/favicon.ico")
def favicon():
    return "", 204

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
        'message': 'Serviço Web Bucket',
        'bucket_name': os.getenv('BUCKET_NAME', 'default_bucket'),
        'bucket_folder': os.getenv('BUCKET_FOLDER', './documents')
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info("A iniciar inicialização do BucketWebService")
    try:
        bucket_service = BucketWebService()
        logger.info("BucketWebService inicializado, a configurar aplicação Flask")
        bucket_service.set_app(app)
        logger.info("A iniciar aplicação Flask")
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        logger.error(f"Falha ao iniciar aplicação Flask: {str(e)}")
        raise