import ollama
import json
from tqdm import tqdm
import re

input_file = r'C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\gun_violence_incidents.jsonl'
output_file = r'C:\Users\tange\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\gun_violence_incidents_PT.jsonl'
target_language = 'português de Portugal'

# List of names and gangs to preserve
names_to_preserve = [
    "Sokovian Syndicate", "Iron Claw Brotherhood", "Black Vipers", "Ghost Shadows",
    "Sokovia", "Novi Grad", "Ravenska", "Vilkor", "Baron’s Peak", "Zakovia",
    "Aleksandr Petrov", "Maria Ivanov", "Dmitri Novak", "Alexander Rykov",
    "Natalia Orlov", "Viktor Zolotov", "Alexei Petrov", "Nadia Ivanova",
    "Marko Novik", "Alexei Borsov", "Ivan Petrov", "Maria Kuznetsova",
    "Olga Ivanova", "Andrei Volkov", "John Dobrov", "Elena Markovic",
    "Ivan Todorov", "John Keller", "Emma Linwood", "Marco Benedetti",
    "Marko Petrovic", "Irina Kovac", "Dmitri Ivanov", "Natalia Romanov",
    "Tomás Verzović", "Jelena Radović"
]

# Count total lines for progress tracking
with open(input_file, 'r', encoding='utf-8') as infile:
    total_lines = sum(1 for _ in infile)

current_line = 0
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in tqdm(infile, total=total_lines, desc="Translating"):
        current_line += 1
        data = json.loads(line.strip())
        
        # Translate the 'title' field
        title = data.get('title')
        if title:
            prompt_title = (
                f"Traduza o seguinte texto para {target_language}, mantendo os nomes próprios e os nomes de gangues "
                f"({', '.join(names_to_preserve)}) inalterados: {title}"
            )
            response_title = ollama.chat(
                model='gemma3:4b',
                messages=[{'role': 'user', 'content': prompt_title}]
            )
            translated_title = response_title['message']['content']
            # Post-process to translate standalone "syndicate" to "sindicato"
            translated_title = re.sub(r'\b[Ss]yndicate\b(?<!Sokovian Syndicate)', 'sindicato', translated_title, flags=re.IGNORECASE)
            data['title'] = translated_title

        # Translate the 'report' field
        report = data.get('report')
        if report:
            prompt_report = (
                f"Traduza o seguinte texto para {target_language}, mantendo os nomes próprios e os nomes de gangues "
                f"({', '.join(names_to_preserve)}) inalterados: {report}"
            )
            response_report = ollama.chat(
                model='gemma3:4b',
                messages=[{'role': 'user', 'content': prompt_report}]
            )
            translated_report = response_report['message']['content']
            # Post-process to translate standalone "syndicate" to "sindicato"
            translated_report = re.sub(r'\b[Ss]yndicate\b(?<!Sokovian Syndicate)', 'sindicato', translated_report, flags=re.IGNORECASE)
            data['report'] = translated_report

        # Write the updated data to the output file
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write('\n')

        # Print progress every 5 lines or at the end
        if current_line % 5 == 0 or current_line == total_lines:
            print(f"Processed {current_line}/{total_lines} lines ({(current_line/total_lines)*100:.1f}%)")