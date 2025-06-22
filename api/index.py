from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

app = FastAPI(
    title="AI Chatbot API",
    description="A business intelligence chatbot powered by AI",
    version="1.0.0"
)

# Initialize chatbot
try:
    from chatbot_simple import SimpleChatBot
    chatbot = SimpleChatBot()
    print("✅ Chatbot initialized successfully")
except Exception as e:
    print(f"❌ Error initializing chatbot: {e}")
    chatbot = None

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat request and return the bot's response"""
    if chatbot is None:
        return {"error": "Chatbot not initialized", "details": "Please check the server logs"}
    
    try:
        response = chatbot.process_input(request.query)
        return {"response": response}
    except Exception as e:
        return {"error": f"Error processing request: {str(e)}"}

@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running. Use POST /chat to interact with the bot."}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    status = "healthy" if chatbot is not None else "degraded"
    return {"status": status, "service": "ai-chatbot", "chatbot_initialized": chatbot is not None}

@app.get("/debug")
async def debug():
    """Debug endpoint to check environment variables and configuration"""
    api_key = os.getenv("OPENAI_API_KEY")
    api_key_status = "✅ Set" if api_key else "❌ Not set"
    api_key_preview = f"{api_key[:10]}..." if api_key and len(api_key) > 10 else "N/A"
    
    return {
        "openai_api_key": api_key_status,
        "api_key_preview": api_key_preview,
        "chatbot_initialized": chatbot is not None,
        "environment": "production"
    }

@app.get("/test")
async def test():
    """Test endpoint to verify the API is working"""
    return {"message": "API is working!", "timestamp": "now"}