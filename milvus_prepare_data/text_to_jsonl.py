import json
import re

# Function to convert a text file to a JSONL file
def txt_to_jsonl(txt_file_path, jsonl_file_path):
    try:
        with open(txt_file_path, 'r') as txt_file, open(jsonl_file_path, 'w') as jsonl_file:
            id = 0
            for line in txt_file:
                # Remove trailing newline character
                line = line.rstrip()

                # Skip empty lines and lines that start with '#'
                if line and not line.startswith('#'):
                    #get rid of all the bad stuff
                    clean_line = line.replace('"', '').replace("ü", "ue").replace("ä", "ae").replace("ö", "oe").replace("ß", "ss").replace("{", "").replace("}", "")
                    

                    json_obj = {"id": str(id), "text": clean_line}
                    jsonl_file.write(json.dumps(json_obj))
                    jsonl_file.write('\n')
                    id += 1

    except FileNotFoundError:
        print(f'File {txt_file_path} not found.')

# Use the function
txt_to_jsonl('data.txt', 'output.jsonl')
