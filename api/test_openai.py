import os
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        print("🔄 Testing OpenAI API connection...")
        response = completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10,
            timeout=10
        )
        print(f"✅ OpenAI API working! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    test_openai_connection() 