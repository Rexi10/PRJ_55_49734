import logging
import httpx

logger = logging.getLogger(__name__)

class AINode:
    def __init__(self):
        self.buckets = []  # List of {'name': str, 'url': str, 'status': str} dictionaries

    def register_bucket(self, bucket_name: str, bucket_url: str) -> bool:
        try:
            if any(b['name'] == bucket_name for b in self.buckets):
                logger.warning(f"Bucket {bucket_name} already registered")
                return False
            # Add status field
            self.buckets.append({'name': bucket_name, 'url': bucket_url, 'status': 'ready'})
            logger.info(f"Registered bucket {bucket_name} at {bucket_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to register bucket {bucket_name}: {str(e)}")
            return False

    def get_buckets(self):
        return self.buckets

    async def forward_query(self, query: str, k: int, selected_buckets=None):
        results = {}
        buckets_to_query = self.buckets
        if selected_buckets:
            buckets_to_query = [b for b in self.buckets if b['name'] in selected_buckets]
        async with httpx.AsyncClient() as client:
            for bucket in buckets_to_query:
                try:
                    url = f"{bucket['url']}/query"
                    response = await client.post(url, json={"query": query, "k": k})
                    if response.status_code == 200:
                        results[bucket['name']] = response.json().get("results", [])
                    else:
                        logger.warning(f"Bucket {bucket['name']} returned status {response.status_code}")
                        results[bucket['name']] = []
                except Exception as e:
                    logger.error(f"Error querying bucket {bucket['name']}: {str(e)}")
                    results[bucket['name']] = []
        return results
