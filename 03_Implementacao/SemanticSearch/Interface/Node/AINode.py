import logging
import httpx
import threading
import time

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

logger = logging.getLogger(__name__)

class AINode:
    def __init__(self):
        self.buckets = []
        # Start healthcheck thread
        threading.Thread(target=healthcheck, args=(self.buckets,), daemon=True).start()

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

    async def forward_query(self, query, k, selected_buckets):
        results = {}
        async with httpx.AsyncClient() as client:
            for bucket in self.buckets:
                if bucket['name'] in selected_buckets:
                    if not bucket.get('alive', True):
                        results[bucket['name']] = [{"error": "Bucket unreachable or offline."}]
                        continue
                    if not bucket.get('processing_complete', False):
                        results[bucket['name']] = [{"error": "Bucket is still processing documents."}]
                        continue
                    try:
                        url = f"{bucket['url']}/query"
                        print(f"Sending query to {bucket['url']}/query")
                        resp = await client.post(url, json={"query": query, "k": k}, timeout=10)
                        if resp.status_code == 200:
                            data = resp.json()
                            results[bucket['name']] = data.get("results", [])
                            # Remove or comment out this line:
                            # results[bucket['name'] + "_query_time"] = data.get("query_time")
                        else:
                            results[bucket['name']] = [{"error": f"Bucket returned status {resp.status_code}"}]
                    except Exception as e:
                        results[bucket['name']] = [{"error": f"Bucket unreachable: {str(e)}"}]
        return results

    async def update_bucket_statuses(self):
        async with httpx.AsyncClient() as client:
            for bucket in self.buckets:
                try:
                    resp = await client.get(f"{bucket['url']}/status", timeout=3)
                    bucket['processing_complete'] = resp.json().get('processing_complete', False)
                except Exception:
                    bucket['processing_complete'] = False

def healthcheck(buckets):
    while True:
        for bucket in buckets:
            try:
                r = requests.get(f"{bucket['url']}/status", timeout=2)
                bucket['alive'] = r.status_code == 200
                bucket['processing_complete'] = r.json().get('processing_complete', False)
                logger.info(f"Healthcheck: {bucket['name']} alive={bucket['alive']}")
            except Exception:
                bucket['alive'] = False
                bucket['processing_complete'] = False
        time.sleep(30)

@app.route("/query", methods=["POST"])
def query_endpoint():
    logger.info("Received query request")