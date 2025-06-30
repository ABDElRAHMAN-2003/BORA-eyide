# BORA: Business Intelligence RAG-Powered Chatbot System
## Technical Documentation for Research Paper

### Abstract
This document provides comprehensive technical documentation for BORA (Business Intelligence Assistant), a Retrieval-Augmented Generation (RAG) powered chatbot system designed for business intelligence applications. The system integrates MongoDB for data storage, Pinecone for vector search, and GPT-4o-mini for natural language generation, providing context-aware responses for fraud analysis, market insights, and revenue analytics.

---

## 1. System Architecture

### 1.1 Overview
BORA employs a modern microservices architecture with the following key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   MongoDB       │    │   Pinecone      │
│   (Vercel)      │◄──►│   (Data Store)  │◄──►│   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hugging Face  │    │   YAML Config   │    │   GPT-4o-mini   │
│   (Embeddings)  │    │   (Agents/Tasks)│    │   (LLM)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 Core Components

#### 1.2.1 Frontend Interface
- **Technology**: FastAPI REST API
- **Deployment**: Vercel serverless functions
- **Endpoint**: `/chat` (POST method)
- **Request Format**: JSON with `query` field
- **Response Format**: JSON with `response`, `context`, `user_pref`, and `system_prompt`

#### 1.2.2 Data Storage Layer
- **Primary Database**: MongoDB Atlas
- **Collections**:
  - `Fraud_LLM_Input`: Fraud analysis input documents
  - `Revenue_LLM_Input`: Revenue analytics input documents
  - `Market_LLM_Input`: Market analysis input documents
  - `Fraud_LLM_Output`: Fraud analysis results
  - `Revenue_LLM_Output`: Revenue analytics results
  - `Market_LLM_Output`: Market analysis results
  - `User_Pref`: User preferences and settings

#### 1.2.3 Vector Database
- **Technology**: Pinecone
- **Index Name**: `cornea`
- **Dimensions**: 1024
- **Embedding Model**: `intfloat/multilingual-e5-large`
- **Purpose**: Semantic search and context retrieval

#### 1.2.4 Language Model
- **Model**: GPT-4o-mini (via OpenAI API)
- **Integration**: LiteLLM library
- **Purpose**: Natural language generation and response synthesis

---

## 2. Technical Implementation

### 2.1 RAG Pipeline Architecture

#### 2.1.1 Data Ingestion Process
```python
def upsert_mongo_collection(collection_name, prefix):
    """
    Extracts documents from MongoDB collections and upserts to Pinecone
    - Reads 'content' field from input documents
    - Generates 1024-dim embeddings using Hugging Face
    - Stores vectors with metadata in Pinecone
    """
```

#### 2.1.2 Embedding Generation
```python
def get_hf_embedding(text):
    """
    Generates embeddings using Hugging Face Inference API
    - Model: intfloat/multilingual-e5-large
    - Output: 1024-dimensional vectors
    - Handles text preprocessing and error cases
    """
```

#### 2.1.3 Context Retrieval
```python
def query_pinecone(query_text, top_k=3):
    """
    Performs semantic search in Pinecone
    - Embeds user query
    - Retrieves top-k most similar documents
    - Returns relevant context for LLM
    """
```

### 2.2 Dynamic System Prompt Generation

#### 2.2.1 Configuration Management
The system uses YAML-based configuration for agents and tasks:

**agents.yaml**:
```yaml
cornea:
  role: "AI Assistant (Jarvis-like)"
  goal: "Be a helpful, conversational AI assistant"
  backstory: "Advanced AI assistant inspired by Jarvis from Iron Man"
```

**tasks.yaml**:
```yaml
chat_response:
  description_template: "Respond to user input naturally..."
  expected_output: "A natural, conversational response..."
```

#### 2.2.2 Prompt Construction
```python
system_prompt = f"""
ROLE: {agent_config['role']}
GOAL: {agent_config['goal']}
BACKSTORY: {agent_config['backstory']}

TASK DESCRIPTION:
{task_config['description_template'].format(relevant_data=relevant_data)}

EXPECTED OUTPUT: {task_config['expected_output']}
"""
```

### 2.3 Error Handling and Resilience

#### 2.3.1 Comprehensive Error Handling
- **YAML Configuration**: Fallback configuration if files unavailable
- **MongoDB Operations**: Graceful degradation if connection fails
- **Pinecone Queries**: Helpful messages when no data available
- **LLM Calls**: Fallback responses if API fails
- **Embedding Generation**: Error logging and recovery

#### 2.3.2 Data Validation
- Text preprocessing and validation
- Embedding dimension verification (1024-dim)
- Empty vector detection and handling
- API response validation

---

## 3. Technologies and Dependencies

### 3.1 Core Technologies
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Web Framework | FastAPI | 0.115.9 | REST API and request handling |
| ASGI Server | Uvicorn | 0.34.3 | Production server |
| Data Validation | Pydantic | 2.11.7 | Request/response validation |
| Environment | python-dotenv | 1.1.0 | Environment variable management |
| LLM Integration | LiteLLM | 1.72.0 | Multi-provider LLM access |
| Configuration | PyYAML | 6.0.2 | YAML file parsing |
| Vector DB | Pinecone | 2.2.4 | Vector storage and search |
| HTTP Client | Requests | Latest | API communication |
| Scheduler | APScheduler | 3.10.4 | Background task scheduling |
| Database | PyMongo | 4.6.1 | MongoDB operations |
| Embeddings | HuggingFace Hub | 0.20.3 | Model inference |

### 3.2 External Services
- **MongoDB Atlas**: Cloud-hosted NoSQL database
- **Pinecone**: Managed vector database service
- **Hugging Face**: Model inference API
- **OpenAI**: GPT-4o-mini language model
- **Vercel**: Serverless deployment platform

---

## 4. Data Flow and Processing

### 4.1 End-to-End Request Processing

1. **User Query Reception**
   ```python
   @app.post("/chat")
   async def chat(request: ChatRequest):
   ```

2. **Context Retrieval**
   - Query embedding generation
   - Pinecone semantic search
   - Relevant document extraction

3. **User Preference Integration**
   - MongoDB query for latest preferences
   - Context enrichment with user data

4. **System Prompt Construction**
   - YAML configuration loading
   - Dynamic prompt template filling
   - Context and preferences integration

5. **LLM Response Generation**
   - GPT-4o-mini API call
   - Response synthesis and formatting

6. **Response Delivery**
   - Structured JSON response
   - Error handling and fallbacks

### 4.2 Background Data Synchronization

```python
def sync_to_pinecone():
    """
    Scheduled background task for MongoDB → Pinecone sync
    - Runs every 10,000 minutes (configurable)
    - Upserts input documents and latest outputs
    - Maintains vector database freshness
    """
```

---

## 5. Performance and Scalability

### 5.1 Performance Optimizations
- **Vector Dimension**: 1024-dim embeddings for optimal search quality
- **Batch Processing**: Efficient bulk upserts to Pinecone
- **Caching**: Environment variable caching and connection pooling
- **Error Recovery**: Graceful degradation and fallback mechanisms

### 5.2 Scalability Features
- **Serverless Architecture**: Automatic scaling on Vercel
- **Asynchronous Processing**: Non-blocking request handling
- **Background Tasks**: Scheduled data synchronization
- **Modular Design**: Easy component replacement and extension

### 5.3 Monitoring and Logging
- **Comprehensive Logging**: Detailed error tracking and debugging
- **Health Checks**: `/health` endpoint for system monitoring
- **Debug Endpoints**: Development and troubleshooting tools
- **Error Reporting**: Structured error responses with details

---

## 6. Security and Privacy

### 6.1 Security Measures
- **Environment Variables**: Secure API key management
- **Input Validation**: Pydantic model validation
- **Error Sanitization**: Safe error message handling
- **HTTPS**: Secure communication via Vercel

### 6.2 Data Privacy
- **No Data Persistence**: Stateless serverless functions
- **Secure Connections**: Encrypted database connections
- **API Key Protection**: Environment-based credential management

---

## 7. Deployment and Configuration

### 7.1 Deployment Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        Vercel Platform                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   API Gateway   │  │  Serverless     │  │  Environment │ │
│  │   (api/index.py)│  │  Functions      │  │  Variables   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Environment Configuration
Required environment variables:
```bash
PINECONE_API_KEY=your_pinecone_api_key
HF_TOKEN=your_huggingface_token
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=your_mongodb_connection_string
```

### 7.3 Configuration Files
- **vercel.json**: Vercel deployment configuration
- **requirements.txt**: Python dependencies
- **src/config/agents.yaml**: Agent definitions
- **src/config/tasks.yaml**: Task templates

---

## 8. Research Contributions

### 8.1 Novel Features
1. **Dynamic Agent Configuration**: YAML-based agent personality management
2. **Multi-Modal Context Integration**: Business data + user preferences
3. **Resilient RAG Pipeline**: Comprehensive error handling and fallbacks
4. **Real-time Data Synchronization**: Background MongoDB → Pinecone sync

### 8.2 Technical Innovations
1. **Hybrid Embedding Strategy**: Hugging Face + Pinecone integration
2. **Contextual Prompt Engineering**: Dynamic system prompt generation
3. **Modular Architecture**: Pluggable components for easy extension
4. **Production-Ready Error Handling**: Graceful degradation strategies

### 8.3 Business Intelligence Applications
1. **Fraud Analysis**: Real-time fraud pattern detection and analysis
2. **Market Intelligence**: Market trend analysis and insights
3. **Revenue Analytics**: Financial performance analysis and reporting
4. **User Preference Learning**: Personalized response generation

---

## 9. Future Enhancements

### 9.1 Planned Improvements
- **Multi-Modal Support**: Image and document processing
- **Real-time Streaming**: WebSocket-based real-time responses
- **Advanced Analytics**: Business intelligence dashboard integration
- **Multi-language Support**: Internationalization and localization

### 9.2 Scalability Roadmap
- **Microservices Architecture**: Component separation and independent scaling
- **Caching Layer**: Redis integration for performance optimization
- **Load Balancing**: Multiple instance deployment
- **Advanced Monitoring**: APM and performance analytics

---

## 10. Conclusion

BORA represents a comprehensive implementation of a RAG-powered chatbot system specifically designed for business intelligence applications. The system demonstrates the effectiveness of combining modern cloud services, advanced language models, and robust error handling to create a production-ready AI assistant.

Key achievements include:
- **Robust Architecture**: Production-ready with comprehensive error handling
- **Scalable Design**: Serverless deployment with automatic scaling
- **Business Focus**: Specialized for fraud, market, and revenue analytics
- **User-Centric**: Personalized responses based on user preferences
- **Research-Ready**: Well-documented and extensible for academic research

The system serves as a foundation for further research in conversational AI, business intelligence, and RAG system optimization.

---

## Appendix A: API Reference

### A.1 Chat Endpoint
**POST** `/chat`

**Request Body:**
```json
{
  "query": "string"
}
```

**Response Body:**
```json
{
  "response": "string",
  "context": "string",
  "user_pref": "string",
  "system_prompt": "string"
}
```

### A.2 Health Check Endpoint
**GET** `/health`

**Response Body:**
```json
{
  "status": "healthy",
  "service": "crewai-chatbot"
}
```

---

## Appendix B: Configuration Examples

### B.1 Agent Configuration
```yaml
cornea:
  role: "AI Assistant (Jarvis-like)"
  goal: "Be a helpful, conversational AI assistant"
  backstory: "Advanced AI assistant inspired by Jarvis from Iron Man"
```

### B.2 Task Configuration
```yaml
chat_response:
  description_template: "Respond to user input naturally..."
  expected_output: "A natural, conversational response..."
```

---

*This documentation provides a comprehensive technical overview of the BORA chatbot system for research and academic purposes.* 