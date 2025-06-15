import logging
import os
import time
from flask import current_app, jsonify
from Manager.EmbeddingManager import EmbeddingManager

logger = logging.getLogger(__name__)

class StartUpController:
    # Inicializa com gestor de embeddings
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    def startup(self):
        start_time = time.time()
        logger.info(f"A verificar pasta de bucket: {os.getenv('BUCKET_FOLDER', './documents')}")
        supported_extensions = {'.txt', '.pdf', '.docx', '.md'}
        document_count = 0
        try:
            bucket_folder = os.getenv('BUCKET_FOLDER', './documents')
            logger.info(f"A verificar se pasta existe: {bucket_folder}")
            # Verifica se existe a pasta
            if not os.path.exists(bucket_folder):
                logger.error(f"Pasta {bucket_folder} não existe")
                with current_app.app_context():
                    return jsonify({'message': f'Pasta {bucket_folder} não existe'}), 500
                
                
            logger.info(f"A iniciar a busca recursiva de {bucket_folder}")
            for root, _, files in os.walk(bucket_folder):
                dir_start = time.time()
                logger.info(f"A verificar diretório: {root}")
                for filename in files:
                    if os.path.splitext(filename)[1].lower() in supported_extensions:
                        logger.info(f"A processar ficheiro: {filename} em {root}")
                        file_path = os.path.join(root, filename)
                        try:
                            file_start = time.time()
                            self.embedding_manager.process_document(file_path)
                            file_time = time.time() - file_start
                            logger.info(f"Ficheiro {filename} processado em {file_time:.2f} segundos")
                            document_count += 1
                        except Exception as e:
                            logger.error(f"Falha ao processar {filename} em {root}: {str(e)}")
                            
                # Regista tempo de processamento do diretório
                logger.info(f"Diretório {root} processado em {time.time() - dir_start:.2f} segundos")
                
                
            total_time = time.time() - start_time
            logger.info(f"Tempo total de inicialização: {total_time:.2f} segundos")
            with current_app.app_context():
                return jsonify({'message': f'Processados {document_count} documentos', 'startup_time': total_time})
            
            
            
        # Trata erros inesperados
        except Exception as e:
            logger.error(f"Inicialização falhou: {str(e)}")
            with current_app.app_context():
                return jsonify({'error': f'Inicialização falhou: {str(e)}'}), 500

    def register_routes(self, app):
        # Define rota para inicialização
        @app.route('/bucket-startup', methods=['GET'])
        def bucket_startup():
            return self.startup()