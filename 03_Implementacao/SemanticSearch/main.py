from WebService.BucketWebService import app
import logging

# Configura o logging na consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('flask.log'), # Log para um ficheiro caso seja necessário
        logging.StreamHandler()
    ]
)

# Suppress HTTP request logs from httpx and httpcore
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

if __name__ == "__main__":
    logging.info("Starting Flask application")
    app.run(debug=False, host="0.0.0.0", port=5000)