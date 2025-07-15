import json
import os
from collections import defaultdict

results_dir = "/app/test/results"
output_dir = "/app/test/comparison_outputs"
os.makedirs(output_dir, exist_ok=True)

# Load results
model_outputs = {}
for file in os.listdir(results_dir):
    if file.endswith(".json"):
        with open(os.path.join(results_dir, file), 'r') as f:
            data = json.load(f)
        model_key = file.replace("results_", "").replace(".json", "")
        model_outputs[model_key] = data

# Compare outputs for each query
query_outputs = defaultdict(dict)
for model, data in model_outputs.items():
    for lang in ["portuguese", "english"]:
        for chunk_size in data[lang]:
            for k in ["K3"]:  # Adjust based on K_VALUES
                sim_key = f"{k}_similarity"
                if sim_key in data[lang][chunk_size][model]:
                    queries = PORTUGUESE_QUERIES if lang == "portuguese" else ENGLISH_QUERIES
                    for i, query in enumerate(queries):
                        query_outputs[f"{lang}_{query}"][model] = data[lang][chunk_size][model][sim_key]

# Detect inconsistencies
with open(os.path.join(output_dir, "output_comparison.txt"), "w") as f:
    for query, outputs in query_outputs.items():
        if len(set(outputs.values())) > 1:  # Different outputs
            f.write(f"Query: {query}\n")
            for model, sim in outputs.items():
                f.write(f"  {model}: {sim}\n")
            f.write("\n")

print("Output comparison completed.")