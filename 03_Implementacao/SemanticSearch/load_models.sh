#!/bin/bash
set -eo pipefail
echo "[$(date)] Starting load_models.sh"

# Start Ollama server
echo "Starting Ollama server..."
ollama serve > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server
timeout=30
until nc -z localhost 11434 || ((timeout-- <= 0)); do
    echo "Waiting for Ollama server..."
    sleep 1
done
if [ $timeout -le 0 ]; then
    echo "[$(date)] Error: Ollama server failed to start within 30 seconds"
    exit 1
fi

# Read models from models.txt
if [ ! -f /root/models.txt ]; then
    echo "[$(date)] Error: models.txt not found at /root/models.txt"
    exit 1
fi

echo "[$(date)] Reading models.txt content:"
cat /root/models.txt

MODELS=()
while IFS= read -r line || [ -n "$line" ]; do
    line=$(echo "$line" | tr -d '\r' | xargs) # Remove whitespace and carriage returns
    if [ -n "$line" ]; then
        MODELS+=("$line")
        echo "[$(date)] Added model to array: $line"
    fi
done < /root/models.txt

if [ ${#MODELS[@]} -eq 0 ]; then
    echo "[$(date)] Error: No models found in /root/models.txt"
    exit 1
fi

echo "[$(date)] Total models to process: ${#MODELS[@]}"
for model in "${MODELS[@]}"; do
    echo "[$(date)] Model in loop: $model"
done

# Pull each model with cleanup between attempts
for MODEL_NAME in "${MODELS[@]}"; do
    echo "[$(date)] Processing model: $MODEL_NAME"

    # Check if model already exists
    if ollama show "$MODEL_NAME" >/dev/null 2>&1; then
        echo "[$(date)] Model $MODEL_NAME already exists, skipping"
        continue
    fi

    for attempt in {1..3}; do
        echo "[$(date)] Attempt $attempt to pull $MODEL_NAME"

        if ollama pull "$MODEL_NAME"; then
            echo "[$(date)] Successfully pulled $MODEL_NAME"
            break
        else
            echo "[$(date)] Pull attempt $attempt failed for $MODEL_NAME"

            # Cleanup failed pull
            ollama rm "$MODEL_NAME" >/dev/null 2>&1 || true

            if [ $attempt -eq 3 ]; then
                echo "[$(date)] Giving up on $MODEL_NAME after 3 attempts"
            else
                sleep $((attempt * 2))  # Exponential backoff
            fi
        fi
    done
done

# Signal model loading completion
touch /root/.ollama/models_loaded
echo "[$(date)] Model loading complete"

# Keep the server running
wait $SERVER_PID