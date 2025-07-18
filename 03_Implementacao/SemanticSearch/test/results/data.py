import json
import matplotlib.pyplot as plt
import os
import numpy as np
import warnings
from collections import defaultdict
import re

# Diretório dos ficheiros de resultados
results_dir = r"C:\Users\tange\Desktop\final\a\03_Implementacao\SemanticSearch\test\results"

# Tamanhos de chunk
chunk_sizes = ["chunk_size_200", "chunk_size_300", "chunk_size_500"]
chunk_labels = ["200", "300", "500"]

# Métricas a considerar
metrics = ["K3_similarity", "K3_noisy_similarity", "K3_query_time", "doc_processing_time"]

# Nomes legíveis para os modelos
MODEL_DISPLAY_NAMES = {
    "all_minilm": "All-MiniLM",
    "nomic_embed_text": "Nomic-Embed",
    "mxbai_embed_large": "MxBAI-Large",
    "snowflake_arctic_embed2": "Snowflake-Arctic",
    "bge_large": "BGE-Large",
    "granite_embedding": "Granite",
    "unclemusclez/jina_embeddings_v2_base_code": "Jina-Embeddings-V2",
    "chevalblanc/acge_text_embedding": "ACGE-Text",
    "jeffh/intfloat_multilingual_e5_large_instruct_f32": "E5-Large",
    "dengcao/Qwen3_Embedding_8B_Q8_0": "Qwen3-8B",
    "dengcao/Qwen3_Embedding_0.6B_F16": "Qwen3-0.6B"
}

output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            warnings.warn(f"Erro ao ler {file_path}: {e}")
            return None

def extract_model_data(data, language, chunk_size, model_key):
    try:
        model_data = data[language][chunk_size][model_key]
        for metric in ["K3_query_time", "doc_processing_time"]:
            if metric in model_data and model_data[metric] < 0:
                model_data[metric] = 0.0
        return model_data
    except KeyError:
        return None

def calculate_avg_similarity(data):
    if "K3_similarity" in data and "K3_noisy_similarity" in data:
        return (data["K3_similarity"] + data["K3_noisy_similarity"]) / 2
    return None

def get_display_name(model_key):
    return MODEL_DISPLAY_NAMES.get(model_key, model_key.replace("_", " ").replace("-", " ").title())

def analyze_file_overlap(all_data, language, output_dir):
    report_path = os.path.join(output_dir, f"{language}_k3_file_overlap.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        for chunk in chunk_sizes:
            chunk_label = chunk_labels[chunk_sizes.index(chunk)]
            overlap_counts = defaultdict(lambda: defaultdict(set))
            for model in all_data[language]:
                model_data = all_data[language][model].get(chunk, {})
                k3_files = model_data.get("K3_top_files", [])
                for idx, query_files in enumerate(k3_files):
                    for file in query_files:
                        overlap_counts[idx][file].add(model)
            f.write(f"\n=== Overlap for Chunk Size {chunk_label} ===\n")
            for query_idx in sorted(overlap_counts.keys()):
                f.write(f"\nQuery {query_idx + 1}\n")
                for file, models in sorted(overlap_counts[query_idx].items(), key=lambda x: (-len(x[1]), x[0])):
                    f.write(f"{file}: selected by {len(models)} models -> {', '.join(sorted(models))}\n")
        f.write("\n=== Per Model Selections ===\n")
        for model in all_data[language]:
            f.write(f"\n{model}:\n")
            for chunk in chunk_sizes:
                model_data = all_data[language][model].get(chunk, {})
                k3_files = model_data.get("K3_top_files", [])
                for idx, files in enumerate(k3_files):
                    f.write(f"  Query {idx + 1} ({chunk}): {', '.join(files)}\n")
    print(f"K3 file overlap report saved to {report_path}")

def generate_consensus_tables(overlap_file_path, output_dir, language="portuguese"):
    with open(overlap_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    chunk_sections = re.split(r'=== Overlap for Chunk Size (\d+) ===', content)
    consensus_per_chunk = {}
    for i in range(1, len(chunk_sections), 2):
        chunk_size = chunk_sections[i]
        chunk_text = chunk_sections[i + 1]
        query_blocks = re.split(r'\nQuery \d+', chunk_text)[1:]
        model_consensus_counts = defaultdict(int)
        for block in query_blocks:
            files = re.findall(r'(.+?): selected by (\d+) models -> (.+)', block)
            if not files:
                continue
            top_file = max(files, key=lambda x: int(x[1]))
            top_file_models = [m.strip() for m in top_file[2].split(',')]
            for model in top_file_models:
                model_consensus_counts[model] += 1
        sorted_counts = sorted(model_consensus_counts.items(), key=lambda x: x[1], reverse=True)
        consensus_per_chunk[chunk_size] = sorted_counts
    for chunk_size, model_counts in consensus_per_chunk.items():
        table_path = os.path.join(output_dir, f"{language}_consensus_table_chunk_{chunk_size}.txt")
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write(f"Consensus Table for Chunk Size {chunk_size}\n")
            f.write(f"{'Rank':<5} {'Model':<25} {'Selections'}\n")
            f.write("-" * 40 + "\n")
            for rank, (model, count) in enumerate(model_counts, 1):
                f.write(f"{rank:<5} {model:<25} {count}\n")
        print(f"Consensus table for chunk size {chunk_size} saved to {table_path}")

def plot_global_bar_metric(language, metric, data, output_dir):
    plt.figure(figsize=(14, 8))
    model_names = list(data.keys())
    x = np.arange(len(model_names))
    width = 0.25
    for i, chunk in enumerate(chunk_sizes):
        values = [data[model][chunk].get(metric, 0) if chunk in data[model] else 0 for model in model_names]
        plt.bar(x + i * width, values, width, label=chunk_labels[i])
    plt.title(f"{metric.replace('_', ' ').title()} by Model ({language.capitalize()})")
    plt.xlabel("Models")
    plt.ylabel(metric.replace('_', ' ').title())
    if metric in ["K3_similarity", "K3_noisy_similarity", "avg_similarity"]:
        plt.ylim(0.5, 1)
    plt.xticks(x + width, model_names, rotation=45, ha="right")
    plt.legend(title="Chunk Size")
    plt.grid(True, linestyle="--", alpha=0.6)  # Added grid
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{metric}_global_bar.png"), dpi=300)
    plt.close()

def plot_per_model_metrics(language, data, output_base_dir):
    for model in data:
        model_data = data[model]
        model_dir = os.path.join(output_base_dir, language, "per_model", model)
        os.makedirs(model_dir, exist_ok=True)
        for metric in metrics + ["avg_similarity"]:
            values = []
            labels = []
            for chunk in chunk_sizes:
                if chunk in model_data:
                    val = model_data[chunk].get(metric, None)
                    if val is not None:
                        values.append(val)
                        labels.append(chunk_labels[chunk_sizes.index(chunk)])
            if values:
                plt.figure(figsize=(6, 4))
                plt.bar(labels, values, color='steelblue')
                plt.title(f"{metric.replace('_', ' ').title()} ({model})")
                plt.xlabel("Chunk Size")
                plt.ylabel(metric.replace('_', ' ').title())
                if metric in ["K3_similarity", "K3_noisy_similarity", "avg_similarity"]:
                    plt.ylim(0.5, 1)
                plt.grid(True, linestyle="--", alpha=0.6)  # Added grid
                plt.tight_layout()
                filename = os.path.join(model_dir, f"{metric}.png")
                plt.savefig(filename, dpi=300)
                plt.close()

def plot_avg_similarity_vs_query_time(language, data, output_dir):
    plt.figure(figsize=(12, 8))
    all_x_vals = []
    all_y_vals = []
    color_map = plt.get_cmap('tab20')
    model_list = list(data.keys())
    for idx, model in enumerate(model_list):
        x_vals, y_vals = [], []
        for chunk in chunk_sizes:
            if chunk in data[model]:
                model_data = data[model][chunk]
                x = model_data.get("K3_query_time", 0)
                y = model_data.get("avg_similarity", 0)
                x_vals.append(x)
                y_vals.append(y)
                all_x_vals.append(x)
                all_y_vals.append(y)
        if len(x_vals) == 3 and len(y_vals) == 3:
            color = color_map(idx % 20)
            plt.fill(x_vals, y_vals, color=color, alpha=0.2, label="_nolegend_", zorder=1)
            x_vals.append(x_vals[0])
            y_vals.append(y_vals[0])
            plt.plot(x_vals, y_vals, marker='o', label=model, color=color, zorder=2)
    plt.grid(True, linestyle="--", alpha=0.6)  # Grid already present
    if all_x_vals and all_y_vals:
        x_mid = np.mean(all_x_vals)
        y_mid = np.mean(all_y_vals)
        plt.axvline(x=x_mid, color='gray', linestyle='--', linewidth=1, zorder=0)
        plt.axhline(y=y_mid, color='gray', linestyle='--', linewidth=1, zorder=0)
    plt.title(f"Avg Similarity vs Query Time ({language.capitalize()})")
    plt.xlabel("Query Time (s)")
    plt.ylabel("Avg Similarity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"avg_similarity_vs_query_time.png"), dpi=300)
    plt.close()

# Processamento
all_data = {"portuguese": {}, "english": {}}
for file in os.listdir(results_dir):
    if not file.endswith(".json"):
        continue
    data = load_json(os.path.join(results_dir, file))
    if not data:
        continue
    if "portuguese" in data and "chunk_size_200" in data["portuguese"]:
        model_key = next(iter(data["portuguese"]["chunk_size_200"]))
    else:
        continue
    display_name = get_display_name(model_key)
    for language in ["portuguese", "english"]:
        if language not in data:
            continue
        if display_name not in all_data[language]:
            all_data[language][display_name] = {}
        for chunk in chunk_sizes:
            if chunk not in data[language]:
                continue
            model_data = extract_model_data(data, language, chunk, model_key)
            if model_data:
                all_data[language][display_name][chunk] = model_data
                avg_sim = calculate_avg_similarity(model_data)
                if avg_sim:
                    model_data["avg_similarity"] = avg_sim

for language in ["portuguese", "english"]:
    lang_data = all_data[language]
    lang_dir = os.path.join(output_dir, language)
    os.makedirs(lang_dir, exist_ok=True)
    for metric in metrics + ["avg_similarity"]:
        plot_global_bar_metric(language, metric, lang_data, lang_dir)
    plot_avg_similarity_vs_query_time(language, lang_data, lang_dir)
    analyze_file_overlap(all_data, language, lang_dir)
    overlap_path = os.path.join(lang_dir, f"{language}_k3_file_overlap.txt")
    generate_consensus_tables(overlap_path, lang_dir, language)
    plot_per_model_metrics(language, lang_data, output_dir)

print(f"\n✅ Todos os gráficos e relatórios foram guardados em: {output_dir}")