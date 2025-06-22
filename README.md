# CrewAI Chatbot

A business intelligence chatbot powered by CrewAI that can analyze fraud data, market trends, and revenue metrics.

## Features

- **Fraud Analysis**: Analyze suspicious transactions and security patterns
- **Market Intelligence**: Get insights on market trends and trading data
- **Revenue Analytics**: Understand financial performance and earnings
- **Conversational AI**: Natural language interaction with business data

## Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd u
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   python -m uvicorn src.main:app --reload --port 8001
   ```

6. **Test the API**
   - Visit `http://localhost:8001` for the API root
   - Visit `http://localhost:8001/docs` for interactive API documentation
   - Send POST requests to `http://localhost:8001/chat` with JSON body: `{"query": "your question here"}`

## Deployment to Railway (Free)

Railway is a great free platform for deploying Python applications. Here's how to deploy:

### Option 1: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway project**
   ```bash
   railway init
   ```

4. **Set environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Deploy via GitHub Integration

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure environment variables**
   - In your Railway project dashboard, go to "Variables"
   - Add `OPENAI_API_KEY` with your OpenAI API key

4. **Deploy**
   - Railway will automatically deploy your application
   - You'll get a public URL like `https://your-app-name.railway.app`

## API Endpoints

- `GET /` - API root and status
- `GET /health` - Health check endpoint
- `POST /chat` - Main chat endpoint
  - Request body: `{"query": "your question"}`
  - Response: `{"response": "bot response"}`

## Example Usage

```bash
# Test the chat endpoint
curl -X POST "https://your-app-name.railway.app/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest fraud patterns?"}'
```

## Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `PORT` (optional): Port for the application (Railway sets this automatically)

## Project Structure

```
u/
├── src/
│   ├── main.py          # FastAPI application
│   ├── chatbot.py       # Core chatbot logic
│   ├── config/          # YAML configuration files
│   └── data/           # Data files for analysis
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment configuration
├── railway.json       # Railway-specific settings
└── runtime.txt        # Python version specification
```

## Free Deployment Alternatives

If Railway doesn't work for you, here are other free options:

1. **Render** - Similar to Railway, good for Python apps
2. **Heroku** - Free tier available (with limitations)
3. **Vercel** - Great for frontend, can work with Python
4. **Netlify** - Primarily for frontend, but can work with serverless functions

## Troubleshooting

- **Port issues**: Make sure your app uses `$PORT` environment variable
- **API key errors**: Verify your OpenAI API key is set correctly
- **Import errors**: Ensure all dependencies are in `requirements.txt`
- **Build failures**: Check that your Python version is compatible

## Support

For deployment issues, check:
- Railway documentation: https://docs.railway.app
- FastAPI documentation: https://fastapi.tiangolo.com
- CrewAI documentation: https://docs.crewai.com # BORA-eyide
