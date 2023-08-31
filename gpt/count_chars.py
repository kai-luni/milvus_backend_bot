def count_characters_in_file(filename):
    total_characters = 0
    with open(filename, 'r') as file:
        for line in file:
            total_characters += len(line)
    return total_characters

filename = 'phat_sharepoint.jsonl'
total_chars = count_characters_in_file(filename)

print(f"Total characters in {filename}: {total_chars}")