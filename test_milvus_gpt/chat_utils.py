from typing import Any, List, Dict
import openai
import requests

import logging
logging.basicConfig(filename='my_application.log', level=logging.DEBUG)


def query_database(query_prompt: str, bearer_token: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input questions.
    """
    url = "http://20.16.150.252:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
    }
    data = {"queries": [{"query": query_prompt, "top_k": 8}]}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


def apply_prompt_template(question: str) -> str:
    """
        A helper function that applies additional template on user's question.
        Prompt engineering could be done here to improve the result. Here I will just use a minimal example.
    """
    prompt = f"""
        By considering above input from me, answer the question: {question}
    """
    return prompt


def call_chatgpt_api(user_question: str, chunks: List[str]) -> Dict[str, Any]:
    """
    Call chatgpt api with user's question and retrieved chunks.
    """
    # Send a request to the GPT-3 API
    messages = list(
        map(lambda chunk: {
            "role": "user",
            "content": chunk
        }, chunks))
    question = apply_prompt_template(user_question)
    messages.append({"role": "user", "content": question})
    response = openai.ChatCompletion.create(
        engine="gpt-35-turbo-version0301",
        messages=messages,
        max_tokens=4096,
        temperature=0.7,  # High temperature leads to a more creative response.
    )
    return response


def ask(user_question: str, bearer_token_db: str) -> Dict[str, Any]:
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

    Returns:
    Dict[str, Any]: A dictionary containing the generated response. The actual message content is located at the "choices"[0]["message"]["content"] location within the dictionary.

    Note: The function assumes a specific structure of the returned results from both the database and the ChatGPT API.
    """

    # Get chunks from database.
    chunks_response = query_database(user_question, bearer_token_db)
    chunks = []
    for result in chunks_response["results"]:
        for inner_result in result["results"]:
            #innter_text = inner_result["text"]
            chunks.append(inner_result["text"])

    logging.info(">>>>>> User's questions: %s", user_question)
    logging.info(">>>>>> Retrieved chunks: %s", chunks)
    response = call_chatgpt_api(user_question, chunks)
    logging.info(">>>>>> Response: %s", response)

    return response["choices"][0]["message"]["content"]