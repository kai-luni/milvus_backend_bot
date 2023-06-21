import os
from typing import Any, List, Dict
import openai
import requests

import logging
logging.basicConfig(filename='my_application.log', level=logging.DEBUG)

bearer_token = os.environ['BEARER_TOKEN']

def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input questions.
    """
    url = "http://0.0.0.0:8000/query"
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
    

if __name__ == "__main__":
    while True:
        user_query = input("Enter your question: ")
        for result in query_database(user_query)["results"]:
            print(result)