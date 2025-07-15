import os
import subprocess

models = [
    "nomic-embed-text",
    "all-minilm-l6-v2"
]

os.environ["PORTUGUESE_TEST_DIR"] = "/app/buckets/bucket4"
os.environ["ENGLISH_TEST_DIR"] = "/app/buckets/bucket1"

for model in models:
    os.environ["MODEL_NAME"] = model
    os.environ["MODEL_KEY"] = model.replace(":", "_").replace("-", "_")
    print(f"Testing model: {model}")
    try:
        subprocess.run(["python", "/app/test/test_model.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error testing model {model}: {e}")
        continue