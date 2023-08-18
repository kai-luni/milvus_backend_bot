import json
from typing import Any, List, Dict
import openai
import requests

import logging
logging.basicConfig(filename='my_application.log', level=logging.DEBUG)





def apply_prompt_template(question: str) -> str:
    """
        A helper function that applies additional template on user's question.
        Prompt engineering could be done here to improve the result. Here I will just use a minimal example.
    """
    prompt_test = f"""
        --------------
        {question}
        --------------

        Hier drueber stehen erst eine Menge Informationen und dann eine Frage.
        Wenn in dem text hier am Anfang nichts relevantes zur Frage steht, dann gebe das wichtigste Wort der Frage
        mit dreimal > davor zurueck.
        Wenn in der Frage nach einer Person gefragt wird, dann antworte nur mit dem namen mit dreimal > davor, 
        ohne sonst etwas zu schreiben. Auch keine Zeichen wie Punkte oder so.
    """

    prompt = f"""
        Du bist ein Assistent, der die Informationen hier drueber nutzt, um Fragen zu beantworten. Beantworte die Fragen so ausgiebig wie moeglich mit den vorhandenen informationen. Wenn die Information im Text nicht vorhanden ist sage: 'Es tut mir leid, ich kenne die Antwort nicht.' {question}
    """
    return prompt

def call_chatgpt_api(user_question: str, chunks: List[str] = None) -> Dict[str, Any]:
    """
    Call chatgpt API with user's question and retrieved chunks.
    
    Parameters:
    - user_question (str): The user's question to ask the model.
    - chunks (List[str], optional): A list of context chunks to prepend before the user's question.
    
    Returns:
    - Dict[str, Any]: The response from the GPT-3 API.
    """
    
    messages = [{"role": "user", "content": chunk} for chunk in (chunks or [])]
    messages.append({"role": "user", "content": user_question})
    
    try:
        response = openai.ChatCompletion.create(
            engine="gpt-35-turbo-version0301",
            messages=messages,
            max_tokens=800,
            temperature=0.5,
        )
        return response
    except Exception as e:
        # Handle the exception as required, for now, just printing it
        print(f"Error occurred: {e}")
        return {}


def ask(user_question: str, bearer_token_db: str, server_ip: str, max_characters_extra_info = 16000, chunks = None) -> Dict[str, Any]:
    """
    This function is designed to handle user's questions by querying a database and generating responses using a ChatGPT API.

    It performs the following steps:
    1. Queries a database using the user's question and a bearer token to get relevant text chunks.
    2. Logs the user's question and the retrieved chunks for tracking and debugging purposes.
    3. Calls the ChatGPT API with the user's question and the retrieved chunks to generate a response.
    4. Logs the generated response.
    5. Returns the first choice from the generated response.

    Parameters:
    user_question (str): The user's question that needs to be answered.
    bearer_token_db (str): The bearer token to authenticate and interact with the vector database.
    server_ip (str): ip of the server

    Returns:
    Dict[str, Any]: A dictionary containing the generated response. The actual message content is located at the "choices"[0]["message"]["content"] location within the dictionary.

    Note: The function assumes a specific structure of the returned results from both the database and the ChatGPT API.
    """
    if chunks is None:
        # Get chunks from database.
        chunks_response = query_database(user_question, bearer_token_db, server_ip)
        chunks = []
        char_counter = 0
        for result in chunks_response["results"]:
            for inner_result in result["results"]:
                innter_text = inner_result["text"]
                char_counter = char_counter + len(innter_text)
                if char_counter > max_characters_extra_info:
                    continue
                logging.info(f">>>>>> Add following info to question: {innter_text}")
                chunks.append(innter_text)

    logging.info(">>>>>> User's questions: %s", user_question)
    response = call_chatgpt_api(apply_prompt_template(user_question), chunks)

    return response["choices"][0]["message"]["content"]

def ask_direct_search(user_question: str) -> Dict[str, Any]:
    logging.info(">>>>>> User's questions: %s", user_question)
    response = call_chatgpt_api(f"""{user_question} ---- Wenn in der Frage oben nach einer Person gefragt wurde, dann schreibe nur den Namen der Person. 
                                Wenn nach einem Fachbegriff gefragt wurde, dann schreibe nur den Fachbegriff, ohne Fachbegriff zu sagen. 
                                Ansonsten schreibe nur die Wichtigsten Keywords des Satzes heraus.""")
    return response["choices"][0]["message"]["content"]

def search_jsonl(file_path: str, search_text: str):
    """
    Search for words in the text field of a .jsonl file and return matching entries.
    
    Parameters:
    - file_path (str): Path to the .jsonl file.
    - search_text (str): Space-separated words to search for. Special characters 
                         (ä, ü, ö, ß) will be replaced with (ae, ue, oe, ss).
    
    Returns:
    - list: Entries sorted by the number of search words matched in descending order.
    """
    search_text = search_text.lower().replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe').replace('ß', 'ss')
    search_words = [word.lower() for word in search_text.split()]
    
    entries_with_counts = []

    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            entry_text_lower = entry.get('text', '').lower()
            match_count = sum(entry_text_lower.count(word) for word in search_words)
            if match_count:
                entries_with_counts.append((entry, match_count))
    
    sorted_entries = [entry for entry, count in sorted(entries_with_counts, key=lambda x: x[1], reverse=True)]
                
    return sorted_entries

def query_database(query_prompt: str, bearer_token: str, server_ip) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input questions.
    """
    url = f"http://{server_ip}:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }
    data = {"queries": [{"query": query_prompt, "top_k": 22}]}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")