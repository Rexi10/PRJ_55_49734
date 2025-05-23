import json
import re
import os

input_file = r'C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\gun_violence_incidents_PT.jsonl'
output_dir = r'C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\output_txt'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Patterns to remove unwanted text (expanded to handle variations)
patterns_to_remove = [
    r"Aqui está a tradução do texto para português de Portugal, mantendo (os nomes próprios e nomes de gangues|todos os nomes próprios e nomes de gangues) inalterados:.*?(?=\n\n|$)",
    r"\*\*Observação:.*?(?=\n\n|$)",
    r"\*\*Nota:.*?(?=\n\n|$)",
    r"Espero que (isto ajude|esta tradução seja útil)!",
    r"É importante notar que, embora a tradução seja precisa em termos de conteúdo, a terminologia.*?(?=\n\n|$)",
    r"\[Nota: Este relatório é construído com base em elementos fictícios e não se relaciona com eventos reais.\]",
    r"\(Note: A tradução procura ser o mais literal possível, preservando a estrutura e o tom original do texto.\)",
    r"\(A tradução do título mantém a precisão e o impacto do original, enfatizando a natureza da ação.\)",
    r"Ou, de forma um pouco mais fluida:.*?(?=\n\n|$)",
    r"Esta tradução procura ser o mais fiel possível ao original, mantendo a estrutura e o tom.*?(?=\n\n|$)"
]

with open(input_file, 'r', encoding='utf-8') as infile:
    for idx, line in enumerate(infile):
        data = json.loads(line.strip())
        gang = data.get('gang', 'Unknown')
        title = data.get('title', '')
        report = data.get('report', '')

        # Combine title and report
        content = f"{title}\n\n{report}"

        # Remove unwanted patterns
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

        # Clean up extra newlines and spaces
        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        # Generate output filename
        output_filename = os.path.join(output_dir, f"incident_{idx+1}_{gang.replace(' ', '_')}.txt")

        # Write to file
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.write(content)

print(f"Generated {idx+1} text files in {output_dir}")