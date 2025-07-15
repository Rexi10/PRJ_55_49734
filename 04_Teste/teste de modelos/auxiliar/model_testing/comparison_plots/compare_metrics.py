import json
import matplotlib.pyplot as plt
import os
import numpy as np

# Diretório dos arquivos de resultados
results_dir = r"/04_Teste/teste de modelos/auxiliar/model_testing/results"

# Lista de ficheiros com dimensões de embedding
files = [
    {"name": "results_medcpt-article.json", "label": "MedCPT Article"},
    {"name": "results_nomic-embed.json", "label": "Nomic Embed"},
    {"name": "results_all-minilm.json", "label": "All MiniLM"},
    {"name": "results_medcpt-query.json", "label": "MedCPT Query"},
    {"name": "results_mxbai-embed.json", "label": "MxBAI Embed"},
    {"name": "results_avrsfr-embed.json", "label": "AVRSFR Embed"},
    {"name": "results_snowflake-embed2.json", "label": "Snowflake Embed2"}
]

# Tamanho do chunk
chunk_size = "chunk_size_300"

# Diretório de saída
output_dir = "comparison_plots"
os.makedirs(output_dir, exist_ok=True)

# Dados para plotagem
similarities = []
query_times = []
labels = []
colors = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']

for i, file_info in enumerate(files):
    filename = os.path.join(results_dir, file_info["name"])
    model_name = file_info["label"]

    # Verifica se o arquivo existe
    if not os.path.exists(filename):
        print(f"Arquivo {filename} não encontrado. Ignorando.")
        continue

    # Carrega dados JSON
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            json_str = ''.join(lines[1:]).strip()
            data = json.loads(json_str)
    except json.JSONDecodeError:
        print(f"Erro ao parsear JSON em {filename}. Ignorando.")
        continue

    # Extrai dados para Português, chunk_size_300
    try:
        # Adjust the key to match the exact model name in JSON if different
        adjusted_model_name = model_name.lower().replace(" ", "-")
        if adjusted_model_name == "snowflake-embed2":
            adjusted_model_name = "snowflake-embed2"  # Keep as is for this file
        portuguese_data = data["portuguese"][chunk_size][adjusted_model_name]
        similarities.append(portuguese_data["K3_similarity"])
        query_times.append(portuguese_data["K3_query_time"])
        labels.append(model_name)
    except KeyError as e:
        print(f"Chave {e} não encontrada em {filename} para chunk_size_300. Ignorando.")
        continue

# Define limites para dividir em quadrantes
x_median = np.median(query_times) if query_times else 0.03
y_median = np.median(similarities) if similarities else 0.7

# Cria o gráfico de dispersão
plt.figure(figsize=(12, 8))
for i, (qt, sim, label) in enumerate(zip(query_times, similarities, labels)):
    plt.scatter(qt, sim, s=100, color=colors[i % len(colors)], edgecolor='black', alpha=0.7, label=label if i == 0 else "")
    plt.annotate(label, (qt, sim), fontsize=12, ha='right', va='bottom', xytext=(5, 5), textcoords='offset points')

# Adiciona linhas para dividir em quadrantes
plt.axvline(x=x_median, color='black', linestyle='--', alpha=0.5)
plt.axhline(y=y_median, color='black', linestyle='--', alpha=0.5)

# Adiciona rótulos para os quadrantes com melhor formatação
plt.text(x_median/1.32, y_median + 0.05, 'Similaridade Alta\nTempo de Consulta Baixo', 
         fontsize=10, ha='center', va='bottom', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
plt.text(x_median / 1.32, y_median - 0.05, 'Similaridade Baixa\nTempo de Consulta Baixo', 
         fontsize=10, ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
plt.text(x_median * 2.4, y_median + 0.05, 'Similaridade Alta\nTempo de Consulta Alto', 
         fontsize=10, ha='center', va='bottom', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
plt.text(x_median * 2.4, y_median - 0.05, 'Similaridade Baixa\nTempo de Consulta Alto',
         fontsize=10, ha='center', va='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

plt.title("Similaridade Média K3 vs Tempo de Consulta K3 (Português, Chunk Size 300)", fontsize=14, pad=15)
plt.xlabel("Tempo de Consulta K3 (segundos)", fontsize=12)
plt.ylabel("Similaridade Média K3", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.7)
plt.legend(fontsize=10, loc='best', framealpha=0.9)
plt.tight_layout()

# Salva o gráfico
output_path = os.path.join(output_dir, "similarity_vs_query_time_quadrants.png")
plt.savefig(output_path, dpi=300)
plt.close()

print(f"Gráfico guardado em '{output_path}'.")