import json

# open the jsonl file as a generator of dictionaries
with open("output.jsonl") as jsonl_file:
    data = [json.loads(line) for line in jsonl_file]