import os
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import pinecone
from huggingface_hub import InferenceClient
import requests
import json

# --- CONFIGURATION ---
MONGO_URI = "mongodb+srv://Ali:suy4C1XDn5fHQOyd@nulibrarysystem.9c6hrww.mongodb.net/sample_db"
DB_NAME = "sample_db"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
INDEX_NAME = "cornea"

# --- MONGODB SETUP ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# --- PINECONE SETUP ---
pinecone.init(api_key=PINECONE_API_KEY)
index = pinecone.Index(INDEX_NAME)

# --- HUGGINGFACE HUB CLIENT SETUP ---
hf_client = InferenceClient(token=HF_TOKEN)

# --- EMBEDDING FUNCTION (Hugging Face InferenceClient, 1024-dim) ---
def get_hf_embedding(text):
    if not isinstance(text, str) or not text.strip():
        print(f"[Warning] Skipping empty or invalid text: {repr(text)}")
        return None
    print(f"Embedding text: {repr(text)}")
    embedding = hf_client.feature_extraction(
        text,
        model="intfloat/multilingual-e5-large",
    )
    # Convert ndarray to list if needed
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
    if isinstance(embedding, list) and isinstance(embedding[0], list):
        embedding = embedding[0]
    if len(embedding) != 1024:
        print(f"[Warning] Embedding dimension is {len(embedding)}, expected 1024.")
        return None
    return embedding

# --- UPSERT FUNCTIONS ---
def upsert_mongo_collection(collection_name, prefix):
    docs = list(db[collection_name].find({}))
    pinecone_vectors = []
    for i, doc in enumerate(docs):
        text = doc.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        vector = get_hf_embedding(text)
        if vector is None or all(v == 0.0 for v in vector):
            continue
        pinecone_vectors.append({
            "id": f"{prefix}_{i}",
            "values": vector,
            "metadata": {"text": text}
        })
    if pinecone_vectors:
        index.upsert(vectors=pinecone_vectors)
        print(f"Upserted {len(pinecone_vectors)} docs from {collection_name}")

# Upsert all input collections
def upsert_all_inputs():
    upsert_mongo_collection("Fraud_LLM_Input", "fraud_input")
    upsert_mongo_collection("Revenue_LLM_Input", "revenue_input")
    upsert_mongo_collection("Market_LLM_Input", "market_input")

# Upsert latest output for each
def upsert_latest_output(collection_name, prefix):
    doc = db[collection_name].find_one(sort=[("date", -1)])
    if doc:
        text = doc.get("text")
        if not text:
            doc_copy = {k: v for k, v in doc.items() if k not in ["_id", "__v", "createdAt"]}
            text = json.dumps(doc_copy, default=str)[:2000]
        if not isinstance(text, str):
            text = str(text)
        vector = get_hf_embedding(text)
        if vector is None or all(v == 0.0 for v in vector):
            print(f"[Warning] Skipping upsert for {prefix}_latest due to empty/invalid vector.")
            return
        index.upsert(vectors=[{
            "id": f"{prefix}_latest",
            "values": vector,
            "metadata": {"text": text}
        }])
        print(f"Upserted latest doc from {collection_name}")

def upsert_all_outputs():
    upsert_latest_output("Fraud_LLM_Output", "fraud_output")
    upsert_latest_output("Revenue_LLM_Output", "revenue_output")
    upsert_latest_output("Market_LLM_Output", "market_output")

# --- QUERY FUNCTION FOR CHATBOT ---
def query_pinecone(query_text, top_k=3):
    query_vector = get_hf_embedding(query_text)
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    print("Raw Pinecone results:", results)  # Debug print
    return [match['metadata']['text'] for match in results['matches']]

# --- MAIN PIPELINE ---
if __name__ == "__main__":
    print("Upserting all input documents...")
    upsert_all_inputs()
    print("Upserting latest output documents...")
    upsert_all_outputs()
    print("Done!")
    # Example query
    test_query = "Show me recent fraud patterns"
    print(f"\nQuerying Pinecone for: {test_query}")
    results = query_pinecone(test_query)
    print("Top results:")
    for r in results:
        print("-", r) 