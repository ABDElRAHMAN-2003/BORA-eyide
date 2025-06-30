import os
from pymongo import MongoClient
from pinecone import Pinecone

# --- CONFIGURATION ---
MONGO_URI = "mongodb+srv://Ali:suy4C1XDn5fHQOyd@nulibrarysystem.9c6hrww.mongodb.net/sample_db"
DB_NAME = "sample_db"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "cornea"

# --- MONGODB SETUP ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# --- PINECONE SETUP ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# --- UPSERT FUNCTIONS ---
def upsert_mongo_collection(collection_name, prefix):
    docs = list(db[collection_name].find({}))
    pinecone_vectors = []
    for i, doc in enumerate(docs):
        pinecone_vectors.append({
            "id": f"{prefix}_{i}",
            "values": None,
            "metadata": {"text": doc.get("text", "")}
        })
    if pinecone_vectors:
        index.upsert(vectors=pinecone_vectors, field_map={"text": "text"})
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
        index.upsert(vectors=[{
            "id": f"{prefix}_latest",
            "values": None,
            "metadata": {"text": doc.get("text", "")}
        }], field_map={"text": "text"})
        print(f"Upserted latest doc from {collection_name}")

def upsert_all_outputs():
    upsert_latest_output("Fraud_LLM_Output", "fraud_output")
    upsert_latest_output("Revenue_LLM_Output", "revenue_output")
    upsert_latest_output("Market_LLM_Output", "market_output")

# --- QUERY FUNCTION FOR CHATBOT ---
def query_pinecone(query_text, top_k=3):
    results = index.query(
        vector=None,
        top_k=top_k,
        include_metadata=True,
        field_map={"text": "text"},
        query={"text": query_text}
    )
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