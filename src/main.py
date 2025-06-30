from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.vector_db_pipeline import upsert_all_inputs, upsert_all_outputs, query_pinecone
from pymongo import MongoClient
import yaml
from litellm import completion

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

MONGO_URI = os.getenv("MONGO_URI") or "mongodb+srv://Ali:suy4C1XDn5fHQOyd@nulibrarysystem.9c6hrww.mongodb.net/sample_db"
DB_NAME = "sample_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Load agent and task config from YAML
config_dir = os.path.join(os.path.dirname(__file__), 'config')
try:
    with open(os.path.join(config_dir, 'agents.yaml'), 'r') as f:
        agents_config = yaml.safe_load(f)
    with open(os.path.join(config_dir, 'tasks.yaml'), 'r') as f:
        tasks_config = yaml.safe_load(f)
    
    AGENT_KEY = list(agents_config.keys())[0]
    agent_config = agents_config[AGENT_KEY]
    task_config = tasks_config['chat_response']
except Exception as e:
    print(f"Warning: Could not load YAML config: {e}")
    # Fallback configuration
    agent_config = {
        'role': 'Business Intelligence Assistant',
        'goal': 'Provide helpful business insights and analysis',
        'backstory': 'An AI assistant specialized in business intelligence'
    }
    task_config = {
        'description_template': 'Based on the following relevant data: {relevant_data}\n\nPlease provide a helpful response to the user query.',
        'expected_output': 'A clear, helpful response based on the available context and user preferences.'
    }

app = FastAPI(
    title="CrewAI Chatbot API with Pinecone RAG",
    description="A business intelligence chatbot powered by Pinecone vector search and MongoDB.",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    query: str

# --- Scheduler for Regular Sync ---
def sync_to_pinecone():
    print("[Scheduler] Syncing MongoDB to Pinecone...")
    upsert_all_inputs()
    upsert_all_outputs()
    print("[Scheduler] Sync complete.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_to_pinecone, 'interval', minutes=10000)  # every 30 minutes
    scheduler.start()
    print("[Scheduler] Started for MongoDB → Pinecone sync.")

@app.on_event("startup")
def on_startup():
    # Initial sync on startup
    sync_to_pinecone()
    # Start background scheduler
    start_scheduler()

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat request and return the bot's response"""
    try:
        # 1. Retrieve relevant context from Pinecone
        try:
            relevant_contexts = query_pinecone(request.query)
            context = "\n".join(relevant_contexts) if relevant_contexts else "No relevant context found."
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            context = "Unable to retrieve context at this time."
        
        # 2. Retrieve user preferences from MongoDB
        try:
            user_pref_doc = db["User_Pref"].find_one(sort=[("updatedAt", -1)])
            user_pref = user_pref_doc["description"] if user_pref_doc and "description" in user_pref_doc else "No user preferences found."
        except Exception as e:
            print(f"Error retrieving user preferences: {e}")
            user_pref = "Unable to retrieve user preferences at this time."
        
        # 3. Build system prompt using agent and task config
        try:
            relevant_data = f"User Preferences: {user_pref}\n\nContext: {context}"
            system_prompt = f"""
ROLE: {agent_config['role']}
GOAL: {agent_config['goal']}
BACKSTORY: {agent_config['backstory']}

TASK DESCRIPTION:
{task_config['description_template'].format(relevant_data=relevant_data)}

EXPECTED OUTPUT: {task_config['expected_output']}
"""
        except Exception as e:
            print(f"Error building system prompt: {e}")
            system_prompt = f"Based on the context: {context}\n\nUser preferences: {user_pref}\n\nPlease provide a helpful response."
        
        # 4. Call your LLM as usual (e.g., OpenAI, local model, etc.)
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ]
            
            response = completion(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "context": context, 
                "user_pref": user_pref, 
                "system_prompt": system_prompt
            }
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Fallback response if LLM fails
            return {
                "response": f"Hello! I'm cornea, your AI assistant. I received your query: '{request.query}'. I can see your preference for mangoes! While I'm having some technical issues with my advanced response generation, I'm here to help. What would you like to know about?",
                "context": context, 
                "user_pref": user_pref, 
                "system_prompt": system_prompt,
                "note": "LLM response generation failed, using fallback response"
            }
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {e}")
        return {
            "error": "An error occurred while processing your request",
            "details": str(e),
            "response": "I'm experiencing technical difficulties. Please try again later."
        }

@app.get("/")
async def root():
    return {"message": "CrewAI Chatbot API with Pinecone RAG is running. Use POST /chat to interact with the bot."}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "crewai-chatbot"}

# For Vercel deployment - this is the entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)