import json
import matplotlib.pyplot as plt
import os

# List of files with their embedding dimensions
files = [
    {"name": "results_medcpt-article.json", "dim": 768},
    {"name": "results_nomic-embed.json", "dim": 1024},
    {"name": "results_all-minilm.json", "dim": 384},
    {"name": "results_medcpt-query.json", "dim": 768},
    {"name": "results_mxbai-embed.json", "dim": 768},
    {"name": "results_avrsfr-embed.json", "dim": 4096},
    {"name": "results_snowflake-embed2.json", "dim": 1024}
]

# Metrics to plot
metrics = [
    {"key": "K3_similarity", "title": "Average K3 Similarity", "ylabel": "Average Similarity", "ylim": [0, 1], "fmt": ".3f"},
    {"key": "doc_processing_time", "title": "Doc Processing Time", "ylabel": "Time (seconds)", "ylim": None, "fmt": ".2f"},
    {"key": "K3_query_time", "title": "K3 Query Time", "ylabel": "Time (seconds)", "ylim": [0, 0.07], "fmt": ".4f"}
]

# Chunk sizes
chunk_sizes = ["chunk_size_200", "chunk_size_300", "chunk_size_500"]
chunk_labels = ["200", "300", "500"]

# Output directory
output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

for file_info in files:
    filename = file_info["name"]
    dim = file_info["dim"]
    model_name = filename.replace("results_", "").replace(".json", "")

    # Load JSON data, skipping the first line
    with open(filename, 'r') as f:
        lines = f.readlines()
        json_str = ''.join(lines[1:]).strip()
        data = json.loads(json_str)

    # Extract data for Portuguese
    portuguese_data = data["portuguese"]

    # Data for plotting
    values = {metric["key"]: [] for metric in metrics}
    for chunk in chunk_sizes:
        for metric in metrics:
            key = metric["key"]
            values[key].append(portuguese_data[chunk][model_name][key])

    # Create a separate figure for each metric
    for metric in metrics:
        key = metric["key"]
        plt.figure(figsize=(6, 4))
        bars = plt.bar(chunk_labels, values[key], color=f"C{metrics.index(metric)}", edgecolor="black")
        plt.title(f"{model_name} (Dim: {dim}) - {metric['title']} (Portuguese)")
        plt.ylabel(metric["ylabel"])
        plt.xlabel("Chunk Size")
        plt.grid(True, axis="y", linestyle="--", alpha=0.7)

        # Add value labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:{metric['fmt']}}", 
                     ha='center', va='bottom', fontsize=10)

        # Set y-axis limit
        if metric["ylim"]:
            plt.ylim(metric["ylim"])
        else:
            plt.ylim(0, max(values[key]) * 1.1)  # Dynamic for doc_processing_time, tightened margin

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{model_name}_{key}.png"))
        plt.close()

print(f"Plots saved in '{output_dir}' directory.")