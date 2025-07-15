import os
import subprocess

# Read models from models.txt
def get_models_from_file():
    with open("/app/models.txt", "r") as f:
        models = [line.strip().replace(':latest', '') for line in f if line.strip()]
    if not models:
        raise ValueError("No models found in /app/models.txt")
    return models

os.environ["PORTUGUESE_TEST_DIR"] = "/app/buckets/bucket4"
os.environ["ENGLISH_TEST_DIR"] = "/app/buckets/bucket1"

models = get_models_from_file()

for model in models:
    os.environ["MODEL_NAME"] = model
    os.environ["MODEL_KEY"] = model.replace(":", "_").replace("-", "_")
    print(f"Testing model: {model}")
    try:
        subprocess.run(["python", "/app/test/test_model.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error testing model {model}: {e}")
        continue