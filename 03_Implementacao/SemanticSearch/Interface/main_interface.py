import logging
import os
import asyncio
import requests
from flask import Flask, request, jsonify, Response, redirect
from InterfaceWebService import InterfaceWebService

logger = logging.getLogger(__name__)

app = Flask(__name__)
interface_service = InterfaceWebService()

@app.route("/")
def index():
    # Serve frontend React
    logger.info("Serving frontend React")
    
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
        
    except FileNotFoundError:
        logger.error("index.html não encontrado na pasta templates")
        return jsonify({"error": "Template não encontrado"}), 500
    
    except Exception as e:
        logger.error(f"Falha serving index.html: {str(e)}")
        return jsonify({"error": f"Falha ao servir template: {str(e)}"}), 500

@app.route("/buckets", methods=["GET"])
def get_buckets():
    buckets = interface_service.ai_node.get_buckets()
    all_ready = all(b.get('status', 'ready') == 'ready' for b in buckets)
    return jsonify({"buckets": buckets, "all_ready": all_ready})

@app.route("/query", methods=["POST"])
def query():
    # Processa consulta do utilizador
    logger.info("Recebido pedido de consulta")
    data = request.get_json()
    if not data or "query" not in data:
        logger.warning("Falta 'query' no corpo do pedido")
        return jsonify({"error": "A consulta deve ser uma string não vazia no campo 'query'", "results": []}), 400
    
    query_text = data.get("query", "")
    k = int(data.get("k", 3))
    selected_buckets = data.get("buckets", None)
    if not query_text:
        logger.warning("Consulta vazia recebida")
        return jsonify({"error": "A consulta deve ser uma string não vazia no campo 'query'", "results": []}), 400
    if k < 1:
        logger.warning("Valor de k inválido")
        return jsonify({"error": "k deve ser um inteiro positivo", "results": []}), 400
    
    try:
        results = asyncio.run(interface_service.ai_node.forward_query(query_text, k, selected_buckets))
        if not isinstance(results, dict):
            logger.error(f"Tipo de resultados inválido de forward_query: {type(results)}, valor: {results}")
            return jsonify({"error": "Resposta inválida dos buckets", "results": []}), 500
        flat_results = []
        for bucket_name, bucket_results in results.items():
            if not isinstance(bucket_results, list):
                logger.warning(f"Resultados inválidos de {bucket_name}: {bucket_results}")
                continue
            for result in bucket_results:
                result['bucket_name'] = bucket_name
                flat_results.append(result)
        if not flat_results:
            logger.info("Nenhum resultado de qualquer bucket")
            return jsonify({"results": []}), 200
        logger.info(f"Consulta retornou resultados de {len([r for r in results.values() if r])} buckets")
        return jsonify({"results": flat_results})
    
    except Exception as e:
        logger.error(f"Consulta falhou: {str(e)}", exc_info=True)
        return jsonify({"error": f"Consulta falhou: {str(e)}", "results": []}), 500

@app.route("/ai-node/register", methods=["POST"])
def register_bucket():
    # Regista novo bucket
    logger.info("Recebido pedido de registo do bucket")
    
    
    data = request.get_json()
    if not data or "name" not in data or "url" not in data:
        logger.warning("Falta 'name' ou 'url' no corpo do pedido")
        return jsonify({"error": "Deve fornecer 'name' e 'url'"}), 400
    bucket_name = data["name"]
    bucket_url = data["url"]
    if not bucket_name or not bucket_url:
        logger.warning("Nome ou URL do bucket vazios")
        return jsonify({"error": "Nome e URL do bucket devem ser não vazios"}), 400
    try:
        if success := interface_service.ai_node.register_bucket(
            bucket_name, bucket_url
        ):
            logger.info(f"Bucket {bucket_name} registrado com sucesso")
            return jsonify({"message": f"Bucket {bucket_name} registrado em {bucket_url}"})
        else:
            logger.error(f"Falha ao registrar bucket {bucket_name}")
            return jsonify({"error": f"Falha ao registrar bucket {bucket_name}"}), 500
    except Exception as e:
        logger.error(f"Registro falhou: {str(e)}")
        return jsonify({"error": f"Registro falhou: {str(e)}"}), 500

@app.route("/startup", methods=["GET"])
def startup():
    logger.info("Recebido pedido de verificação de inicialização")
    return jsonify({"message": "Processado"})

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # Redireciona para bucket com o ficheiro
    for bucket in interface_service.ai_node.get_buckets():
        return redirect(f"{bucket['url']}/download/{filename}")
    return jsonify({'error': 'Ficheiro não encontrado'}), 404

@app.route('/download/<bucket>/<path:filename>', methods=['GET'])
def proxy_download(bucket, filename):
    # Proxy para download de ficheiros
    buckets = interface_service.ai_node.get_buckets()
    bucket_info = next((b for b in buckets if b['name'] == bucket), None)
    if not bucket_info:
        return jsonify({'error': 'Bucket não encontrado'}), 404
    bucket_url = bucket_info['url']
    download_url = f"{bucket_url}/download/{filename}"
    try:
        r = requests.get(download_url, stream=True)
        if r.status_code != 200:
            return jsonify({'error': 'Ficheiro não encontrado no bucket'}), 404
        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                "Content-Disposition": f"attachment; filename={filename.split('/')[-1]}"
            },
            content_type=r.headers.get('Content-Type', 'application/octet-stream')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Configura registo de logs
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
    logger.info("Inicialização do InterfaceWebService")
    interface_service = InterfaceWebService()
    logger.info("InterfaceWebService inicializado, a iniciar aplicação Flask")
    app.run(host="0.0.0.0", port=5000, debug=False)