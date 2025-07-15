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

# Read models from models.txt
if [ ! -f /root/models.txt ]; then
    echo "[$(date)] Error: models.txt not found at /root/models.txt"
    exit 1
fi

MODELS=()
while IFS= read -r line; do
    line=$(echo "$line" | tr -d '\r' | xargs) # Remove whitespace and carriage returns
    [ -n "$line" ] && MODELS+=("$line")
done < /root/models.txt

# Pull each model with cleanup between attempts
for MODEL_NAME in "${MODELS[@]}"; do
    echo "[$(date)] Processing model: $MODEL_NAME"

    # Check if model already exists
    if ollama show "$MODEL_NAME" >/dev/null 2>&1; then
        echo "[$(date)] Model $MODEL_NAME already exists, skipping"
        continue
    fi

    for attempt in {1..5}; do
        echo "[$(date)] Attempt $attempt to pull $MODEL_NAME"

        if ollama pull "$MODEL_NAME"; then
            echo "[$(date)] Successfully pulled $MODEL_NAME"
            break
        else
            echo "[$(date)] Pull attempt $attempt failed for $MODEL_NAME"

            # Cleanup failed pull
            ollama rm "$MODEL_NAME" >/dev/null 2>&1 || true

            if [ $attempt -eq 5 ]; then
                echo "[$(date)] Giving up on $MODEL_NAME after 5 attempts"
            else
                sleep $((attempt * 2))  # Exponential backoff
            fi
        fi
    done
done

echo "[$(date)] Model loading complete"
wait $SERVER_PID