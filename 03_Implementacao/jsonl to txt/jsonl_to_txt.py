import pandas as pd
import json
import os

# Define the input JSONL file path
input_file = "gun_violence_incidents.jsonl"

# Read the JSONL file into a list of dictionaries
data = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

# Create a pandas DataFrame
df = pd.DataFrame(data)

# Ensure the output directory exists
output_dir = "incident_reports"
os.makedirs(output_dir, exist_ok=True)

# Iterate through the DataFrame and save each report as a .txt file
for index, row in df.iterrows():
    # Use the title as the filename, sanitized to avoid invalid characters
    filename = row['title'].replace(':', '_').replace('/', '_').replace('?', '').replace('*', '') + '.txt'
    filepath = os.path.join(output_dir, filename)
    
    # Write the report content to a .txt file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(row['report'])

print(f"Successfully created {len(df)} text files in the '{output_dir}' directory.")