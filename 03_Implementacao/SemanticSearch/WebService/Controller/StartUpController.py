import logging
from Manager.StartUpManager import StartUpManager

logger = logging.getLogger(__name__)

class StartUpController:
    def __init__(self, embedding_manager):
        logger.debug("Initializing StartUpController")
        self.startup_manager = StartUpManager(embedding_manager)

    def startup(self) -> dict[str, str]:
        logger.debug("Starting controller")
        count = self.startup_manager.startup()
        return {"message": f"Processed {count} documents"}