import logging
import os
import requests
from Controller.StartUpController import StartUpController
from Controller.QueryController import QueryController
from Manager.EmbeddingManager import EmbeddingManager
from flask import Flask, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.processing_complete = False

class BucketWebService:
    # Inicializa serviço com configurações de bucket
    def __init__(self):
        self.bucket_name = os.getenv("BUCKET_NAME", "default_bucket")
        self.bucket_folder = os.getenv("BUCKET_FOLDER", "./documents")
        self.ai_node_url = os.getenv("AI_NODE_URL", "http://interface:5000/ai-node")
        self.bucket_url = os.getenv("BUCKET_URL", "http://bucket1:5000")
        logger.info("A iniciar BucketWebService")
        
        
        self.embedding_manager = EmbeddingManager()
        self.startup_controller = StartUpController(self.embedding_manager)
        self.query_controller = QueryController(self.embedding_manager)
        self.processing_complete = False

    def set_processing_complete(self, value: bool):
        self.processing_complete = value

    def _register_with_ai_node(self, app):
        # Regista bucket no nó AI
        
        logger.info(f"A registar bucket {self.bucket_name} no AI Node em {self.ai_node_url}/register")
        try:
            response = requests.post(
                f"{self.ai_node_url}/register",
                json={"name": self.bucket_name, "url": self.bucket_url}
            )
            response.raise_for_status()
            logger.info(f"Registo bem-sucedido no AI Node: {response.text}")
            logger.info("A iniciar processamento automático de documentos após registo")
            with app.app_context():
                result = self.startup_controller.startup()
            result_json = result.get_json()
            logger.info(f"Resultado do processamento automático: {result_json.get('message', 'Sem mensagem')}")
            self.set_processing_complete(True)
            app.processing_complete = True
        except Exception as e:
            logger.error(f"Falha ao registar no AI Node: {str(e)}")
            raise

    def set_app(self, app: Flask):
        logger.info("A iniciar registo de rotas")
        # Regista controladores e nó AI
        logger.info(f"Rotas existentes: {[rule.endpoint for rule in app.url_map.iter_rules()]}")
        
        
        
        logger.info("A registar rotas do StartUpController")
        self.startup_controller.register_routes(app)
        logger.info("Rotas do StartUpController registadas")
        
        
        
        logger.info("A registar rotas do QueryController")
        self.query_controller.register_routes(app)
        logger.info("Rotas do QueryController registadas")



        self._register_with_ai_node(app)
        self.register_routes(app)

    def register_routes(self, app):
        # Define endpoint de status
        @app.route("/status", methods=["GET"])
        def status():
            return jsonify({
                "processing_complete": app.processing_complete
            })