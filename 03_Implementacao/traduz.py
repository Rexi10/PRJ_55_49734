import ollama
import json
from tqdm import tqdm

input_file = r'C:\Users\A49734\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\gun_violence_incidents.jsonl'
output_file = r'C:\Users\A49734\Desktop\Projeto final\PRJ_55_49734\03_Implementacao\gun_violence_incidents_PT.jsonl'
target_language = 'português de Portugal'

# Count total lines for progress tracking
with open(input_file, 'r', encoding='utf-8') as infile:
    total_lines = sum(1 for _ in infile)

current_line = 0
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    # Wrap infile with tqdm for progress bar
    for line in tqdm(infile, total=total_lines, desc="Translating"):
        current_line += 1
        data = json.loads(line.strip())
        report = data.get('report')
        if report:
            response = ollama.chat(
                model='gemma3:4b',
                messages=[{'role': 'user', 'content': f'Traduza para {target_language}: {report}'}]
            )
            translated_report = response['message']['content']
            data['translated_report'] = translated_report
            json.dump(data, outfile, ensure_ascii=False)
            outfile.write('\n')
        # Print progress every 5 lines or at the end
        if current_line % 5 == 0 or current_line == total_lines:
            print(f"Processed {current_line}/{total_lines} lines ({(current_line/total_lines)*100:.1f}%)")