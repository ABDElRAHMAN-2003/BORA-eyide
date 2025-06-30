import os
from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
from pinecone import Pinecone
from huggingface_hub import InferenceClient
from litellm import embedding
import requests
import json

# --- CONFIGURATION ---
MONGO_URI = "mongodb+srv://Ali:suy4C1XDn5fHQOyd@nulibrarysystem.9c6hrww.mongodb.net/sample_db"
DB_NAME = "sample_db"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure this is set
INDEX_NAME = "corrnea"  # 1536-dim Pinecone index for OpenAI embeddings

# --- MONGODB SETUP ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# --- PINECONE SETUP ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# --- HUGGINGFACE HUB CLIENT SETUP ---
hf_client = InferenceClient(token=PINECONE_API_KEY)

# --- EMBEDDING FUNCTION (OpenAI text-embedding-ada-002, 1536-dim) ---
def get_openai_embedding(text):
    if not isinstance(text, str) or not text.strip():
        print(f"[Warning] Skipping empty or invalid text: {repr(text)}")
        return None
    print(f"Embedding text: {repr(text)}")
    try:
        result = embedding(
            model="text-embedding-ada-002",
            input=text,
            api_key=OPENAI_API_KEY
        )
        vector = result['data'][0]['embedding']
        if len(vector) != 1536:
            print(f"[Warning] Embedding dimension is {len(vector)}, expected 1536.")
            return None
        print(f"Final embedding length: {len(vector)}")
        return vector
    except Exception as e:
        print(f"Error in get_openai_embedding: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

# --- UPSERT FUNCTIONS ---
def upsert_mongo_collection(collection_name, prefix):
    docs = list(db[collection_name].find({}))
    pinecone_vectors = []
    for i, doc in enumerate(docs):
        text = doc.get("content", "")
        if not isinstance(text, str):
            text = str(text)
        vector = get_openai_embedding(text)
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
        vector = get_openai_embedding(text)
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

# --- CHECK PINECONE DATA ---
def check_pinecone_data():
    """Check if Pinecone index has any data"""
    try:
        stats = index.describe_index_stats()
        total_vector_count = stats.get('total_vector_count', 0)
        print(f"Pinecone index has {total_vector_count} vectors")
        return total_vector_count > 0
    except Exception as e:
        print(f"Error checking Pinecone data: {e}")
        return False

# --- QUERY FUNCTION FOR CHATBOT ---
def query_pinecone(query_text, top_k=3):
    try:
        print(f"Starting Pinecone query for: {query_text}")
        print(f"Pinecone API Key present: {bool(PINECONE_API_KEY)}")
        print(f"OpenAI API Key present: {bool(OPENAI_API_KEY)}")
        
        # Check if Pinecone has data
        has_data = check_pinecone_data()
        if not has_data:
            print("Pinecone index is empty - no data to search")
            return ["No business data available yet. The system is still being populated with your documents."]
        
        query_vector = get_openai_embedding(query_text)
        if query_vector is None:
            print("Failed to get embedding for query")
            return ["Unable to process your query at this time due to technical issues."]
            
        print(f"Query vector generated, length: {len(query_vector)}")
        
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        print("Raw Pinecone results:", results)  # Debug print
        
        if not results.get('matches'):
            return ["No specific business data found for your query. I can help with general questions or you can ask about fraud analysis, market trends, or revenue data."]
            
        return [match['metadata']['text'] for match in results['matches']]
    except Exception as e:
        print(f"Error in query_pinecone: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return ["I'm experiencing technical difficulties accessing the business data. Please try again later."]

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