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
        logging.error(f"Error occurred: {e}")
        raise e


def ask(user_question: str, bearer_token_db: str, server_ip: str, max_characters_extra_info = 16000, source: str = "vector") -> Dict[str, Any]:
    """
    Handles user questions, queries a database, and generates responses using ChatGPT.

    - Queries the database with the user's question.
    - Logs the user's question and the retrieved chunks.
    - Calls ChatGPT with the question and chunks to generate a response.
    - Logs and returns the first generated response.

    Parameters:
    - user_question (str): The user's input question.
    - bearer_token_db (str): Token for database authentication.
    - server_ip (str): IP address of the server.
    - max_characters_extra_info (int, optional): Maximum character limit for extra info. Defaults to 16000.
    - source (str, optional): Data source type. Defaults to "vector".

    Returns:
    - Dict[str, Any]: Contains the generated response in "choices"[0]["message"]["content"].
    """
    chunks = ""
    if source == "vector":
        # Get chunks from database.
        chunks = query_database(user_question, bearer_token_db, server_ip, max_characters_extra_info=max_characters_extra_info)
    else:
        keywords = ask_direct_search(user_question)
        chunks = search_jsonl("/mnt/c/git_linux/milvus_backend_bot/gpt/phat_sharepoint.jsonl", keywords, max_characters_extra_info=max_characters_extra_info)

    logging.info(">>>>>> User's questions: %s", user_question)
    response = call_chatgpt_api(apply_prompt_template(user_question), chunks)

    return response["choices"][0]["message"]["content"]

def ask_direct_search(user_question: str) -> Dict[str, Any]:
    """
    Handles user questions using ChatGPT for direct keyword extraction.

    - Logs the user's question.
    - Calls ChatGPT with the question and specific prompts to extract keywords.
    - Returns the extracted keywords or relevant information.

    Parameters:
    - user_question (str): The user's input question.

    Returns:
    - Dict[str, Any]: Contains the extracted keywords or information in "choices"[0]["message"]["content"].
    """
    logging.info(">>>>>> User's questions: %s", user_question)
    response = call_chatgpt_api(f"""{user_question} ---- Wenn in der Frage oben nach einer Person gefragt wurde, dann schreibe nur den Namen der Person. 
                                Wenn nach einem Fachbegriff gefragt wurde, dann schreibe nur den Fachbegriff, ohne Fachbegriff zu sagen. 
                                Ansonsten schreibe nur die Wichtigsten Keywords des Satzes heraus.""")
    return response["choices"][0]["message"]["content"]

def query_database(query_prompt: str, bearer_token: str, server_ip: str, max_characters_extra_info: int = 16000) -> List[str]:
    """
    Queries a vector database and retrieves relevant text chunks based on the user's input.

    Parameters:
    - query_prompt (str): The user's input question or prompt for querying.
    - bearer_token (str): Authentication token for the database.
    - server_ip (str): IP address of the database server.
    - max_characters_extra_info (int, optional): Max character limit for the combined chunks. Defaults to 16000.

    Returns:
    - List[str]: List of retrieved text chunks.

    Raises:
    - ValueError: If there's an error in the database response.
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

        chunks = []
        char_counter = 0
        for result in result["results"]:
            for inner_result in result["results"]:
                innter_text = inner_result["text"]
                char_counter = char_counter + len(innter_text)
                if char_counter > max_characters_extra_info:
                    continue
                logging.info(f">>>>>> Add following info to question: {innter_text}")
                chunks.append(innter_text)

        # process the result
        return chunks
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")

def search_jsonl(file_path: str, search_text: str, max_characters_extra_info: int = 16000) -> List[str]:
    """
    Search for words in a .jsonl file and return matching entries.
    
    Parameters:
    - file_path (str): Path to the .jsonl file.
    - search_text (str): Words to search for, separated by spaces. Special characters 
                         (ä, ü, ö, ß) are replaced with (ae, ue, oe, ss).
    - max_characters_extra_info (int, optional): Maximum combined character limit for returned entries. 
                                                 Defaults to 16000.
    
    Returns:
    - List[str]: List of entries sorted by the number of search words matched in descending order. 
                 The total character count of the list will be below the 'max_characters_extra_info' threshold.
    """
    search_text = search_text.lower().replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe').replace('ß', 'ss')
    search_words = [word for word in search_text.split()]
    
    entries_with_counts = []

    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            entry_text_lower = entry.get('text', '').lower()
            match_count = sum(entry_text_lower.count(word) for word in search_words)
            if match_count:
                entries_with_counts.append((entry, match_count))
    
    sorted_texts = [entry["text"] for entry, _ in sorted(entries_with_counts, key=lambda x: x[1], reverse=True)]
    
    final_texts = []
    char_counter = 0
    for text in sorted_texts:
        char_counter += len(text)
        if char_counter > max_characters_extra_info:
            break
        final_texts.append(text)
                
    return final_texts