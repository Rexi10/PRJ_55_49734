import json
import matplotlib.pyplot as plt
import os

# Lista de ficheiros com dimensões de embedding
files = [
    {"name": "results_medcpt-article.json", "dim": 768, "label": "medcpt-article"},
    {"name": "results_nomic-embed.json", "dim": 1024, "label": "nomic-embed"},
    {"name": "results_all-minilm.json", "dim": 384, "label": "all-minilm"},
    {"name": "results_medcpt-query.json", "dim": 768, "label": "medcpt-query"},
    {"name": "results_mxbai-embed.json", "dim": 768, "label": "mxbai-embed"},
    {"name": "results_avrsfr-embed.json", "dim": 4096, "label": "avrsfr-embed"},
    {"name": "results_snowflake-embed2.json", "dim": 1024, "label": "snowflake-embed2"}
]

# Métricas para plotar
metrics = [
    {"key": "K3_similarity", "title": "Similaridade Média K3", "ylabel": "Similaridade Média", "ylim": [0, 1], "fmt": ".3f"},
    {"key": "doc_processing_time", "title": "Tempo de Processamento de Documentos", "ylabel": "Tempo (segundos)", "ylim": [0, 42], "fmt": ".2f"},
    {"key": "K3_query_time", "title": "Tempo de Consulta K3", "ylabel": "Tempo (segundos)", "ylim": [0, 0.07], "fmt": ".4f"}
]

# Tamanho do chunk para comparar
chunk_size = "chunk_size_300"

# Diretório de saída
output_dir = "comparison_plots"
os.makedirs(output_dir, exist_ok=True)

# Dados para plotagem
values = {metric["key"]: [] for metric in metrics}
labels = [f"{f['label']} ({f['dim']})" for f in files]

for file_info in files:
    filename = file_info["name"]
    model_name = file_info["label"]

    # Carrega dados JSON, ignorando a primeira linha
    with open(filename, 'r') as f:
        lines = f.readlines()
        json_str = ''.join(lines[1:]).strip()
        data = json.loads(json_str)

    # Extrai dados para Português, chunk_size_300
    portuguese_data = data["portuguese"][chunk_size][model_name]
    for metric in metrics:
        values[metric["key"]].append(portuguese_data[metric["key"]])

# Cria uma figura separada para cada métrica
for metric in metrics:
    key = metric["key"]
    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, values[key], color=f"C{metrics.index(metric)}", edgecolor="black")
    plt.title(f"Comparação de {metric['title']} (Português, chunk_size_300)")
    plt.ylabel(metric["ylabel"])
    plt.xlabel("Modelo (Dimensão do Embedding)")
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.xticks(rotation=45, ha="right")

    # Adiciona etiquetas de valores no topo das barras
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:{metric['fmt']}}", 
                 ha='center', va='bottom', fontsize=9)

    # Define limite do eixo y
    plt.ylim(metric["ylim"])

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"compare_{key}.png"))
    plt.close()

print(f"Gráficos guardados no diretório '{output_dir}'.")