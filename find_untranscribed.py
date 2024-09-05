import csv
import re
import os

def find_and_remove_missing_files(csv_file, wavs_folder):
    file_numbers = set()
    missing_files = []

    # Read the CSV file and extract file numbers
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:
                filename = row[0]
                match = re.search(r'_(\d+)\.wav', filename)
                if match:
                    file_number = int(match.group(1))
                    file_numbers.add(file_number)

    # Find missing numbers and remove corresponding files
    max_number = max(file_numbers)
    for i in range(1, max_number + 1):
        if i not in file_numbers:
            missing_file = f"mem1_{i:04d}.wav"
            missing_files.append(missing_file)
            file_path = os.path.join(wavs_folder, missing_file)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed: {missing_file}")
            else:
                print(f"File not found: {missing_file}")

    return missing_files

# Specify the paths
csv_file_path = 'dataset/metadata.csv'
wavs_folder_path = 'dataset/wavs'

# Find missing files and remove them
missing = find_and_remove_missing_files(csv_file_path, wavs_folder_path)

# Print the results
if missing:
    print("\nThe following .wav files were missing and removed (if found):")
    for file in missing:
        print(file)
else:
    print("No files were missing in the sequence.")