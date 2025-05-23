import logging
import os
import requests
from Controller.StartUpController import StartUpController
from Controller.QueryController import QueryController
from Manager.EmbeddingManager import EmbeddingManager
from flask import Flask, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.processing_complete = False  # Add this line!

class BucketWebService:
    def __init__(self):
        self.bucket_name = os.getenv("BUCKET_NAME", "default_bucket")
        self.bucket_folder = os.getenv("BUCKET_FOLDER", "./documents")
        self.ai_node_url = os.getenv("AI_NODE_URL", "http://interface:5000/ai-node")  # Updated to use service name
        self.bucket_url = os.getenv("BUCKET_URL", "http://bucket1:5000")  # Updated to use service name
        
        logger.info("Starting BucketWebService initialization")
        self.embedding_manager = EmbeddingManager()
        self.startup_controller = StartUpController(self.embedding_manager)
        self.query_controller = QueryController(self.embedding_manager)
        self.processing_complete = False

    def set_processing_complete(self, value: bool):
        self.processing_complete = value

    def _register_with_ai_node(self, app):
        logger.info(f"Registering bucket {self.bucket_name} with AI Node at {self.ai_node_url}/register")
        try:
            response = requests.post(
                f"{self.ai_node_url}/register",
                json={"name": self.bucket_name, "url": self.bucket_url}
            )
            response.raise_for_status()
            logger.info(f"Successfully registered with AI Node: {response.text}")
            logger.info("Starting automatic document processing after registration")
            with app.app_context():
                result = self.startup_controller.startup()
            result_json = result.get_json()  # Parse Response to JSON
            logger.info(f"Automatic processing result: {result_json.get('message', 'No message')}")
            self.set_processing_complete(True)
            app.processing_complete = True  # <-- ADD THIS LINE
        except Exception as e:
            logger.error(f"Failed to register with AI Node: {str(e)}")
            raise

    def set_app(self, app: Flask):
        logger.info("Starting route registration")
        logger.info(f"Existing routes: {[rule.endpoint for rule in app.url_map.iter_rules()]}")
        logger.info("Registering StartUpController routes")
        self.startup_controller.register_routes(app)
        logger.info("StartUpController routes registered")
        logger.info("Registering QueryController routes")
        self.query_controller.register_routes(app)
        logger.info("QueryController routes registered")
        self._register_with_ai_node(app)
        self.register_routes(app)

    def register_routes(self, app):
        @app.route("/status", methods=["GET"])
        def status():
            return jsonify({
                "processing_complete": app.processing_complete  # This must be True after startup
            })
