import os
import openai
import json

# Load config values
with open('config.json') as config_file:
    config_details = json.load(config_file)

chatgpt_model_name = config_details['CHATGPT_MODEL']
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = config_details['OPENAI_API_BASE']
openai.api_version = config_details['OPENAI_API_VERSION']

base_system_message = "You are a helpful assistant."
system_message = f"{base_system_message.strip()}"

def send_message(messages, model_name, max_response_tokens=500):
    response = openai.ChatCompletion.create(
        engine=model_name,
        messages=messages,
        temperature=0.3,
        max_tokens=max_response_tokens,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response['choices'][0]['message']['content']

def print_conversation(messages):
    for message in messages:
        print(f"[{message['role'].upper()}]")
        print(message['content'])
        print()

def chat_with_gpt():
    """
    This function reads a JSONL file line by line, and for each line,
    if the text length is more than 1000 characters, it requests GPT to
    summarize the text to less than 1000 characters. It then prints the
    original and summarized text. The function returns nothing.

    Args:
        None

    Returns:
        None
    """

    updated_data = []  # to store the updated data
    with open('file.jsonl', 'r') as jsonl_file:
        for line in jsonl_file:
            messages = [
                {"role": "system", "content": system_message},
            ]
            data = json.loads(line)  # convert JSON string to Python dictionary
            text = data["text"]
            if len(text) > 1000:
                messages.append({"role": "user", "content": f"please summarize the following text to less than 1000 characters: {text}"})
                response = send_message(messages, chatgpt_model_name)
                data["text"] = response
            updated_data.append(data)

    # write updated data to a new JSONL file
    with open('updated_file.jsonl', 'w') as outfile:
        for entry in updated_data:
            json.dump(entry, outfile)
            outfile.write('\n')
    
if __name__ == "__main__":
    chat_with_gpt()
