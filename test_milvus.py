from datasets import load_dataset

data = load_dataset("squad", split="train")
data = data.to_pandas()
data = data.drop_duplicates(subset=["context"])
print(len(data))



documents = [
    {
        'id': r['id'],
        'text': r['context'],
        'metadata': {
            'title': r['title']
        }
    } for r in data.to_dict(orient='records')
]
documents = [documents[0]]



import os

BEARER_TOKEN = os.environ.get("BEARER_TOKEN") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gS2xvIiwiaWF0IjoxNTE2MjM5MDIyfQ.4rotTfTgaCiamy369WcvJ0LOFZKUilEKKU407A9xXMU"

print(f"token: {BEARER_TOKEN}")


headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}



from tqdm.auto import tqdm
import requests
from requests.adapters import HTTPAdapter, Retry

batch_size = 100
endpoint_url = "http://localhost:8000"
s = requests.Session()

# we setup a retry strategy to retry on 5xx errors
retries = Retry(
    total=5,  # number of retries before raising error
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
s.mount('http://', HTTPAdapter(max_retries=retries))

for i in tqdm(range(0, len(documents), batch_size)):
    i_end = min(len(documents), i+batch_size)
    # make post request that allows up to 5 retries
    res = s.post(
        f"{endpoint_url}/upsert",
        headers=headers,
        json={
            "documents": documents[i:i_end]
        }
    )
    print(f"result: {res.status_code} {res.content}")