import csv
import re
from openai import OpenAI
from dotenv import load_dotenv
import os
import time  

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_row(row):
    # Remove quotes
    row = [field.strip('"') for field in row]
    
    # Remove triple spaces
    row = [re.sub(r'\s{3,}', '', field) for field in row]
    
    return row

def process_batch(rows, client):
    # Join rows into a single string
    text = "\n".join(["|".join(row) for row in rows])
    
    # Use OpenAI to fix vocabulary
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert Spanish writing assistant."},
            {"role": "user", "content": f"Fix the vocabulary in the following text, keeping the same structure and information. If there are words that are missing letters, add them. If there are words that are misspelled, correct them. If there are numbers or dates in the text, keep them how they are written. Just output the metadata, don't add anymore explanation typical of LLMs. Text:\n\n{text}"}
        ]
    )

    print(response)
    
    # Add a 5-second delay after each API call
    time.sleep(5)
    
    # Split the fixed text back into rows
    fixed_text = response.choices[0].message.content

    
    fixed_rows = [row.split("|") for row in fixed_text.split("\n")]
    
    return fixed_rows


input_file = 'dataset/metadata.csv'
output_file = 'dataset/cleaned_metadata.csv'

with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile, delimiter='|')
    writer = csv.writer(outfile, delimiter='|')
    
    batch = []
    for i, row in enumerate(reader, 1):
        cleaned_row = clean_row(row)
        batch.append(cleaned_row)
        
        if i % 100 == 0:
            fixed_batch = process_batch(batch, client)
            writer.writerows(fixed_batch)
            batch = []
    
    # Process any remaining rows
    if batch:
        fixed_batch = process_batch(batch, client)
        writer.writerows(fixed_batch)

print(f"Cleaned and vocabulary-fixed data has been written to {output_file}")
