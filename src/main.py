from fastapi import FastAPI
from pydantic import BaseModel
from .chatbot import ChatBot
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

app = FastAPI(
    title="CrewAI Chatbot API",
    description="A business intelligence chatbot powered by CrewAI",
    version="1.0.0"
)
chatbot = ChatBot()

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat request and return the bot's response"""
    response = chatbot.process_input(request.query)
    return {"response": response}

@app.get("/")
async def root():
    return {"message": "CrewAI Chatbot API is running. Use POST /chat to interact with the bot."}

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