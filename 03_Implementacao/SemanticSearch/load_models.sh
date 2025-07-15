#!/bin/bash
set -eo pipefail
echo "[$(date)] Starting load_models.sh"

# Start Ollama server
echo "Starting Ollama server..."
ollama serve > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server
timeout=60
until nc -z localhost 11434 || ((timeout-- <= 0)); do
    echo "Waiting for Ollama server..."
    sleep 1
done

# Pull model using the official name format
MODEL_NAME="nomic-embed-text"
echo "[$(date)] Pulling model: $MODEL_NAME"

for attempt in {1..3}; do
    if ollama pull $MODEL_NAME; then
        echo "[$(date)] Successfully pulled $MODEL_NAME"
        break
    else
        echo "[$(date)] Attempt $attempt failed for $MODEL_NAME"
        sleep 2
        [ $attempt -eq 3 ] && echo "[$(date)] Failed to pull $MODEL_NAME after 3 attempts"
    fi
done

echo "[$(date)] Model loading complete"
wait $SERVER_PID