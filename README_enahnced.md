# 🦅 Bora - Executive Business Intelligence Chatbot

Bora is an AI-powered executive business intelligence coordinator designed specifically for the Eyide dashboard. It provides comprehensive insights across fraud detection, market analysis, and revenue forecasting domains.

## 👥 Team
- **Development Team**: Magdy, Saif, Julia, Ali, Omar, Amr  
- **Supervisor**: Dr. Noha

## 🚀 Quick Start

### Installation
\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with your OPENAI_API_KEY
\`\`\`

### Usage
\`\`\`bash
# Run the chatbot
python -m src.main

# Or after installation
pip install -e .
bora
\`\`\`

## 📁 Project Structure
\`\`\`
src/
├── data/
│   └── userPref.txt          # Executive preferences
├── __init__.py               # Package initialization
├── chatbot.py               # Main Bora chatbot class
├── main.py                  # CLI interface
├── database_manager.py      # MongoDB connection
└── user_preferences.py      # User preference management
\`\`\`

## 🎯 Features

### Executive-Level Intelligence
- **Comprehensive Business Overview**: Bird's eye view across all domains
- **Personalized Communication**: Addresses executives by name with preferred style
- **Strategic Insights**: Cross-domain analysis and recommendations
- **Real-Time Data**: Direct MongoDB integration with your existing models

### Domain Expertise
- **🛡️ Fraud Intelligence**: Risk assessment, transaction monitoring, prevention strategies
- **📊 Market Intelligence**: Competitive analysis, SWOT insights, positioning strategies  
- **💰 Revenue Intelligence**: Forecasting, growth analysis, optimization recommendations

## 💬 Sample Queries

### Quick Commands
- `summary` or `dashboard` - Comprehensive executive briefing
- `fraud` - Fraud risk analysis
- `market` - Market intelligence summary
- `revenue` - Revenue performance overview

### Natural Language Queries
- *"What are our biggest business risks this quarter?"*
- *"How do we compare to competitors in the market?"*
- *"Show me the correlation between fraud risks and revenue growth"*
- *"What strategic actions should we prioritize?"*

## ⚙️ Configuration

### User Preferences (`src/data/userPref.txt`)
\`\`\`
Executive Name: Your Name
Preferred Greeting: Good morning
Communication Style: professional
Team: Magdy, Saif, Julia, Ali, Omar, Amr
Supervisor: Dr. Noha
Focus Areas: revenue, fraud, market
Dashboard Layout: comprehensive
\`\`\`

### Environment Variables (`.env`)
\`\`\`
OPENAI_API_KEY=your_openai_api_key_here
\`\`\`

## 🔗 Data Integration

Bora connects to your existing MongoDB collections:
- `Fraud_LLM_Input` - Fraud detection data
- `Market_LLM_Input` - Market analysis data
- `Revenue_LLM_Input` - Revenue forecasting data

The system uses your pre-built model outputs to provide executive-level insights.

## 🛠️ Technical Architecture

- **CrewAI Framework**: Multi-agent coordination
- **MongoDB Integration**: Real-time data access
- **Modular Design**: Separated concerns for maintainability
- **Executive Focus**: High-level insights, not technical details

## 📞 Support

For technical support or questions about Bora, please contact the Eyide development team.

---
*Developed with ❤️ by the Eyide Team*
