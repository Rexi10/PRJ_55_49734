import logging
from urllib.parse import urljoin
from flask import Flask, jsonify, request, redirect
import httpx
from Node.AINode import AINode
import asyncio

logger = logging.getLogger(__name__)

class InterfaceWebService:
    def __init__(self):
        logger.debug("Initializing InterfaceWebService")
        self.ai_node = AINode()
        self.app = None
        logger.info("InterfaceWebService initialization complete")

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
            data = request.get_json()
            query = data.get('query')
            k = data.get('k', 3)
            if not query or not isinstance(k, int) or k < 1:
                logger.warning("Invalid query or k")
                return jsonify({'error': 'Invalid query or k', 'results': []}), 400
            try:
                results = await self.ai_node.forward_query(query, k)
                if not isinstance(results, dict):
                    logger.error(f"Invalid results type from forward_query: {type(results)}, value: {results}")
                    return jsonify({'error': 'Invalid response from buckets', 'results': []}), 500
                flat_results = []
                for bucket_name, bucket_results in results.items():
                    if not isinstance(bucket_results, list):
                        logger.warning(f"Invalid results from {bucket_name}: {bucket_results}")
                        continue
                    for result in bucket_results:
                        result['bucket_name'] = bucket_name
                        flat_results.append(result)
                logger.info(f"Returning {len(flat_results)} query results")
                return jsonify({'results': flat_results})
            except Exception as e:
                logger.error(f"Query failed: {str(e)}", exc_info=True)
                return jsonify({'error': f'Query processing failed: {str(e)}', 'results': []}), 500

        @self.app.route('/startup', methods=['GET'])
        async def startup():
            # Check if any bucket has processed documents
            processed = False
            async with httpx.AsyncClient() as client:
                for bucket in self.ai_node.get_buckets():
                    try:
                        response = await client.get(urljoin(bucket['url'], '/bucket-startup'))
                        response.raise_for_status()
                        if "Processed" in response.text:
                            processed = True
                            break
                    except Exception:
                        continue
            return jsonify({'message': f"Documents processed: {processed}"})

        @self.app.route('/download/<path:filename>', methods=['GET'])
        def download(filename):
            for bucket in self.ai_node.get_buckets():
                if any(result.get('location') == filename for result in (request.get_json() or {}).get('results', [])):
                    return redirect(f"{bucket['url']}/download/{filename}")
            return jsonify({'error': 'File not found'}), 404

        @self.app.route('/ai-node/register', methods=['POST'])
        def register_bucket():
            data = request.get_json()
            bucket_name = data.get('bucket_name')
            bucket_url = data.get('bucket_url')
            if bucket_name and bucket_url:
                if self.ai_node.register_bucket(bucket_name, bucket_url):
                    return jsonify({'status': 'success', 'message': f'Bucket {bucket_name} registered'}), 200
                return jsonify({'status': 'error', 'message': 'Registration failed'}), 500
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
