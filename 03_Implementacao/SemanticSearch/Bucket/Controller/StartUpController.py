import logging
import os
import time
from flask import current_app, jsonify
from Manager.EmbeddingManager import EmbeddingManager

logger = logging.getLogger(__name__)

class StartUpController:
    def __init__(self, embedding_manager: EmbeddingManager):
        logger.debug("Initializing StartUpController")
        self.embedding_manager = embedding_manager

    def startup(self):
        start_time = time.time()
        logger.info(f"Scanning bucket folder: {os.getenv('BUCKET_FOLDER', './documents')}")
        supported_extensions = {'.txt', '.pdf', '.docx', '.md'}
        document_count = 0
        try:
            bucket_folder = os.getenv('BUCKET_FOLDER', './documents')
            logger.info(f"Checking if bucket folder exists: {bucket_folder}")
            if not os.path.exists(bucket_folder):
                logger.error(f"Bucket folder {bucket_folder} does not exist")
                with current_app.app_context():
                    return jsonify({'message': f'Bucket folder {bucket_folder} does not exist'}), 500
            logger.info(f"Starting recursive scan of {bucket_folder}")
            for root, _, files in os.walk(bucket_folder):
                dir_start = time.time()
                logger.info(f"Scanning directory: {root}")
                for filename in files:
                    if os.path.splitext(filename)[1].lower() in supported_extensions:
                        logger.info(f"Processing file: {filename} in {root}")
                        file_path = os.path.join(root, filename)
                        try:
                            file_start = time.time()
                            self.embedding_manager.process_document(file_path)
                            file_time = time.time() - file_start
                            logger.info(f"Processed file {filename} in {file_time:.2f} seconds")
                            document_count += 1
                        except Exception as e:
                            logger.error(f"Failed to process {filename} in {root}: {str(e)}")
                logger.info(f"Processed directory {root} in {time.time() - dir_start:.2f} seconds")
            total_time = time.time() - start_time
            logger.info(f"Total startup time: {total_time:.2f} seconds")
            with current_app.app_context():
                return jsonify({'message': f'Processed {document_count} documents', 'startup_time': total_time})
        except Exception as e:
            logger.error(f"Startup failed: {str(e)}")
            with current_app.app_context():
                return jsonify({'error': f'Startup failed: {str(e)}'}), 500

    def register_routes(self, app):
        @app.route('/bucket-startup', methods=['GET'])
        def bucket_startup():
            return self.startup()  # Delegate to the startup method