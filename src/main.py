from fastapi import FastAPI
from pydantic import BaseModel
from .chatbot import ChatBot
import uvicorn
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.vector_db_pipeline import upsert_all_inputs, upsert_all_outputs, query_pinecone

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

app = FastAPI(
    title="CrewAI Chatbot API with Pinecone RAG",
    description="A business intelligence chatbot powered by Pinecone vector search and MongoDB.",
    version="1.0.0"
)
chatbot = ChatBot()

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
    scheduler.add_job(sync_to_pinecone, 'interval', minutes=540)  # every 30 minutes
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
    # 1. Retrieve relevant context from Pinecone
    relevant_contexts = query_pinecone(request.query)
    context = "\n".join(relevant_contexts)
    # 2. Use context in your LLM prompt
    system_prompt = f"Use the following context to answer the question:\n{context}\n\nQuestion: {request.query}"
    # 3. Call your LLM as usual (e.g., OpenAI, local model, etc.)
    # response = call_llm(system_prompt, request.query)
    # For demo, just return the context and prompt:
    return {"context": context, "system_prompt": system_prompt}

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

# from dotenv import load_dotenv
# import os
# from .chatbot import ChatBot

# def main():
#     # Load environment variables from .env file
#     load_dotenv()

#     # Verify that the API key is loaded
#     if not os.getenv("OPENAI_API_KEY"):
#         raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

#     chatbot = ChatBot()
#     print("Welcome to the CLI Chatbot! (Type 'exit' to quit)")

#     while True:
#         user_input = input("\nYou: ").strip()

#         if user_input.lower() == 'exit':
#             print("Goodbye!")
#             break

#         if user_input:
#             response = chatbot.process_input(user_input)
#             print(f"\nChatbot: {response}")

# if __name__ == "__main__":
#     main()