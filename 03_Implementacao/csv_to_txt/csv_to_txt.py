import pandas as pd
import os
import math

# Define the path to the CSV file
csv_file = "mtsamples.csv"

# Define the base output directory for text files
base_output_dir = "transcriptions"
os.makedirs(base_output_dir, exist_ok=True)  # Create base directory if it doesn't exist

# Number of files per folder
files_per_folder = 200

# Read the CSV file
df = pd.read_csv(csv_file)

# Calculate the number of folders needed
num_folders = math.ceil(len(df) / files_per_folder)

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    # Get the sample name and transcription
    sample_name = row['sample_name']
    transcription = row['transcription']
    
    # Determine the folder for this file
    folder_num = index // files_per_folder + 1
    folder_name = f"folder_{folder_num}"
    folder_path = os.path.join(base_output_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
    
    # Replace spaces with underscores and create a valid filename
    filename = sample_name.replace(" ", "_").replace("/", "_").replace("-", "_") + ".txt"
    file_path = os.path.join(folder_path, filename)
    
    # Write the transcription to a text file
    with open(file_path, 'w', encoding='utf-8') as f:
        if pd.notna(transcription):  # Check for non-NaN transcription
            f.write(str(transcription))  # Convert to string to handle any potential non-string data
        else:
            f.write("")  # Write empty string for NaN values

print(f"Created {len(df)} text files across {num_folders} folders in the '{base_output_dir}' directory.")