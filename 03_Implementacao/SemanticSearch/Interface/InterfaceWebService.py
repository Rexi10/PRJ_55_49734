import logging
from urllib.parse import urljoin
from flask import Flask, jsonify, request, redirect
import httpx
from Node.AINode import AINode


logger = logging.getLogger(__name__)

class InterfaceWebService:
    # Inicializa serviço
    def __init__(self):
        logger.debug("A inicializar InterfaceWebService")

        
        self.ai_node = AINode()
        self.app = None
        logger.info("InicializaÃ§Ã£o do InterfaceWebService concluÃ­da")

    def set_app(self, app: Flask):
        self.app = app
        self.register_routes()

    def register_routes(self):
        @self.app.route('/buckets', methods=['GET'])
        def get_buckets():
            buckets = self.ai_node.get_buckets()
            return jsonify({'buckets': buckets})

        @self.app.route('/query', methods=['POST'])
        async def query():
            # Processa consulta assincrona
            data = request.get_json()
            query = data.get('query')
            k = data.get('k', 3)
            if not query or not isinstance(k, int) or k < 1:
                logger.warning("Consulta ou k invalidos")
                return jsonify({'error': 'Consulta ou k invalidos', 'results': []}), 400
            try:
                results = await self.ai_node.forward_query(query, k)
                if not isinstance(results, dict):
                    logger.error(f"Tipo de resultados invÃ¡lido de forward_query: {type(results)}, valor: {results}")
                    return jsonify({'error': 'Resposta invÃ¡lida dos buckets', 'results': []}), 500
                flat_results = []
                for bucket_name, bucket_results in results.items():
                    if not isinstance(bucket_results, list):
                        logger.warning(f"Resultados invalidos de {bucket_name}: {bucket_results}")
                        continue
                    for result in bucket_results:
                        result['bucket_name'] = bucket_name
                        flat_results.append(result)
                logger.info(f"A retornar {len(flat_results)} resultados de consulta")
                return jsonify({'results': flat_results})
            except Exception as e:
                logger.error(f"Consulta falhou: {str(e)}", exc_info=True)
                return jsonify({'error': f'Falha no processamento da consulta: {str(e)}', 'results': []}), 500

        @self.app.route('/startup', methods=['GET'])
        async def startup():
            # Verifica estado de inicializaÃ§Ã£o dos buckets
            async with httpx.AsyncClient() as client:
                buckets = self.ai_node.get_buckets()
                if not buckets:
                    return jsonify({'message': 'Nenhum bucket registado'}), 200
                all_processed = True
                for bucket in buckets:
                    try:
                        response = await client.get(urljoin(bucket['url'], '/bucket-startup'), timeout=5)
                        response.raise_for_status()
                        if "Processed" not in response.text:
                            all_processed = False
                            break
                    except Exception as e:
                        logger.error(f"Falha ao verificar bucket {bucket['name']}: {str(e)}")
                        all_processed = False
                        break
                message = "Processados todos os documentos" if all_processed else "Buckets ainda a processar"
                return jsonify({'message': message})

        @self.app.route('/download/<path:filename>', methods=['GET'])
        def download(filename):
            for bucket in self.ai_node.get_buckets():
                if any(result.get('location') == filename for result in (request.get_json() or {}).get('results', [])):
                    return redirect(f"{bucket['url']}/download/{filename}")
            return jsonify({'error': 'Ficheiro nÃ£o encontrado'}), 404

        @self.app.route('/ai-node/register', methods=['POST'])
        def register_bucket():
            # Regista bucket no nÃ³ AI
            data = request.get_json()
            bucket_name = data.get('bucket_name')
            bucket_url = data.get('bucket_url')
            if bucket_name and bucket_url:
                if self.ai_node.register_bucket(bucket_name, bucket_url):
                    return jsonify({'status': 'success', 'message': f'Bucket {bucket_name} registado'}), 200
                return jsonify({'status': 'error', 'message': 'Falha no registo'}), 500
            return jsonify({'status': 'error', 'message': 'Dados invalidos'}), 400