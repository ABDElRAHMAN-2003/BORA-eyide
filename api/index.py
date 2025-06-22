from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.chatbot import ChatBot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

app = FastAPI(
    title="CrewAI Chatbot API",
    description="A business intelligence chatbot powered by CrewAI",
    version="1.0.0"
)

# Initialize chatbot
try:
    chatbot = ChatBot()
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    chatbot = None

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat request and return the bot's response"""
    if chatbot is None:
        return {"error": "Chatbot not initialized"}
    
    try:
        response = chatbot.process_input(request.query)
        return {"response": response}
    except Exception as e:
        return {"error": f"Error processing request: {str(e)}"}

@app.get("/")
async def root():
    return {"message": "CrewAI Chatbot API is running. Use POST /chat to interact with the bot."}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "crewai-chatbot"} 