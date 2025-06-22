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

def get_fallback_response(user_input):
    """Provide intelligent fallback responses when OpenAI is unavailable"""
    user_input_lower = user_input.lower()
    
    # Greeting responses
    if any(word in user_input_lower for word in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
        return "Hello! I'm your business intelligence assistant. I can help you with fraud analysis, market insights, and revenue analytics. What would you like to know?"
    
    # Identity questions
    if any(word in user_input_lower for word in ['name', 'who are you', 'who built you', 'created by']):
        return "I'm BORA, a business intelligence assistant designed to help with fraud detection, market analysis, and revenue insights. I'm currently running in fallback mode due to connection issues."
    
    # Business data questions
    if any(word in user_input_lower for word in ['fraud', 'fraudulent', 'suspicious', 'security']):
        return "I can help you with fraud analysis! Based on our data, we've identified several patterns including unusual transaction volumes, geographic anomalies, and time-based suspicious activities. Would you like me to elaborate on any specific aspect when the connection is restored?"
    
    if any(word in user_input_lower for word in ['market', 'trend', 'stock', 'trading', 'price']):
        return "For market analysis, I can provide insights on trading patterns, market trends, and price movements. Our data shows various market indicators and performance metrics. I'll be able to give you detailed analysis once the connection is restored."
    
    if any(word in user_input_lower for word in ['revenue', 'income', 'profit', 'financial', 'money', 'earnings']):
        return "Regarding revenue analytics, I can help you understand financial performance, earnings trends, and profit analysis. Our data includes revenue patterns, growth metrics, and financial indicators. I'll provide detailed insights when the connection is restored."
    
    # Default response
    return "I understand your question about business intelligence. I'm currently experiencing connection issues with my AI service, but I can still help you with general business insights. Please try again in a few moments, or ask me about fraud analysis, market trends, or revenue analytics."

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat request and return the bot's response"""
    if chatbot is None:
        return {"error": "Chatbot not initialized", "details": "Please check the server logs"}
    
    try:
        print(f"Processing request: {request.query}")
        response = chatbot.process_input(request.query)
        print(f"Response generated successfully")
        return {"response": response}
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat endpoint: {error_msg}")
        
        # Check if it's a connection error and provide fallback
        if "Connection error" in error_msg or "APIError" in error_msg:
            fallback_response = get_fallback_response(request.query)
            return {
                "response": fallback_response,
                "note": "This is a fallback response due to connection issues. Please try again later for full AI capabilities."
            }
        
        return {"error": f"Error processing request: {error_msg}"}

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

@app.get("/test-openai")
async def test_openai():
    """Test OpenAI API connectivity directly"""
    try:
        from litellm import completion
        
        # Try different models
        models_to_try = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4"]
        
        for model in models_to_try:
            try:
                print(f"Trying model: {model}")
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": "Say hello"}],
                    max_tokens=10,
                    timeout=10
                )
                
                return {
                    "status": "success",
                    "response": response.choices[0].message.content,
                    "model": model
                }
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        # If all models fail
        return {
            "status": "error",
            "error": "All models failed to connect",
            "error_type": "ConnectionError"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/test")
async def test():
    """Test endpoint to verify the API is working"""
    return {"message": "API is working!", "timestamp": "now"}