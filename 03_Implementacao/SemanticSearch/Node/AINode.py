import logging
import httpx

logger = logging.getLogger(__name__)

class AINode:
    def __init__(self):
        self.buckets = []  # List of {'name': str, 'url': str} dictionaries

    def register_bucket(self, bucket_name: str, bucket_url: str) -> bool:
        try:
            if any(b['name'] == bucket_name for b in self.buckets):
                logger.warning(f"Bucket {bucket_name} already registered")
                return False
            self.buckets.append({'name': bucket_name, 'url': bucket_url})
            logger.info(f"Registered bucket {bucket_name} at {bucket_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to register bucket {bucket_name}: {str(e)}")
            return False

    def get_buckets(self):
        return self.buckets

    async def forward_query(self, query: str, k: int):
        results = {}
        async with httpx.AsyncClient() as client:
            for bucket in self.buckets:
                try:
                    response = await client.post(
                        f"{bucket['url']}/query",
                        json={"query": query, "k": k},
                        timeout=30
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    results[bucket['name']] = json_response.get('results', [])
                except Exception as e:
                    logger.error(f"Failed to query bucket {bucket['name']}: {str(e)}")
                    results[bucket['name']] = []
        logger.debug(f"Forward_query results: {results}")
        return results