#!/bin/bash

# CrewAI Chatbot Deployment Script for Railway
echo "🚀 Starting CrewAI Chatbot deployment to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Initialize Railway project if not already done
if [ ! -f ".railway" ]; then
    echo "📁 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "🔧 Setting up environment variables..."
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    
    if [ ! -z "$OPENAI_API_KEY" ]; then
        railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
        echo "✅ OPENAI_API_KEY set successfully"
    else
        echo "⚠️  OPENAI_API_KEY not found in .env file"
        echo "Please set it manually: railway variables set OPENAI_API_KEY=your_key_here"
    fi
else
    echo "⚠️  .env file not found. Please create one with your OPENAI_API_KEY"
    echo "Example: echo 'OPENAI_API_KEY=your_key_here' > .env"
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at: https://your-app-name.railway.app"
echo "📖 Check the deployment status with: railway status" 