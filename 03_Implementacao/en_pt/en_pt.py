import os
from deep_translator import GoogleTranslator

# Caminhos das pastas
input_folder = r"C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\en_pt\incident_reports"
output_folder = r"C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\en_pt\incident_reports_pt"
os.makedirs(output_folder, exist_ok=True)

def translate_to_portuguese(text):
    translator = GoogleTranslator(source='auto', target='pt')
    return translator.translate(text)

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(input_folder, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Separa o título (primeira linha) do resto
        lines = content.splitlines()
        if lines:
            title = lines[0]
            rest = "\n".join(lines[1:])
            translated_title = translate_to_portuguese(title)
            translated_rest = translate_to_portuguese(rest) if rest.strip() else ""
            translated_content = translated_title + "\n" + translated_rest
        else:
            translated_content = translate_to_portuguese(content)
        # Traduz o nome do arquivo (sem extensão)
        name_only = os.path.splitext(filename)[0]
        translated_name = translate_to_portuguese(name_only)
        for char in r'\/:*?"<>|':
            translated_name = translated_name.replace(char, "_")
        output_path = os.path.join(output_folder, f"{translated_name}.txt")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(translated_content)
        print(f"Arquivo traduzido salvo: {output_path}")