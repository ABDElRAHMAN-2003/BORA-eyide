import os
from pymongo import MongoClient
from typing import Dict, List, Optional
import json

class DatabaseManager:
    def __init__(self):
        self.uri = "mongodb+srv://Ali:suy4C1XDn5fHQOyd@nulibrarysystem.9c6hrww.mongodb.net/sample_db"
        self.db_name = "sample_db"
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            print("✅ Connected to MongoDB successfully")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def get_fraud_data(self) -> Dict:
        """Retrieve fraud analysis data and model outputs"""
        try:
            # Get input data
            input_collection = self.db["Fraud_LLM_Input"]
            input_data = list(input_collection.find({}, {"content": 1, "agent": 1}))
            
            # Sample fraud model output based on your provided structure
            fraud_analysis = {
                "intent": "Suspicious",
                "category": "Risk",
                "fraud_metrics": {
                    "incident_rate": "0.20",
                    "common_patterns": {
                        "Prevalence of Payment Fraud": "18.75% of transactions analyzed were classified as fraudulent, primarily involving high payment amounts.",
                        "High-Risk Cash Out": "The Cash Out transaction type represented a significant risk factor, with 1 out of 4 transactions showing signs of fraud."
                    }
                },
                "analysis": {
                    "cause": "The prevalence of fraudulent transactions was highly attributed to larger amounts being withdrawn via Cash Out, indicating a trend of exploiting vulnerable accounts.",
                    "recommendation": "To mitigate future risks, a multifaceted approach integrating advanced machine learning techniques and heightened scrutiny on high-value transactions is advised."
                },
                "transactions": [
                    {
                        "name": "Transaction 6",
                        "amount": 7107.77,
                        "currency": "USD",
                        "flag": "green",
                        "date": "2025-01-15",
                        "description": "Payment for goods",
                        "category": "PAYMENT",
                        "type": "PURCHASE",
                        "fraud_rate": 0.05
                    },
                    {
                        "name": "Transaction 15",
                        "amount": 229133.94,
                        "currency": "USD",
                        "flag": "red",
                        "date": "2025-02-20",
                        "description": "Large cash out transaction",
                        "category": "CASH_OUT",
                        "type": "WITHDRAWAL",
                        "fraud_rate": 0.85
                    }
                ],
                "fraud_rate_over_time": [
                    {"date": "2025-01-01", "fraud_rate": 0.15},
                    {"date": "2025-02-01", "fraud_rate": 0.2},
                    {"date": "2025-03-01", "fraud_rate": 0.25}
                ]
            }
            
            return {
                "input_data": input_data,
                "analysis_results": [fraud_analysis]
            }
        except Exception as e:
            print(f"Error fetching fraud data: {e}")
            return {"input_data": [], "analysis_results": []}
    
    def get_market_data(self) -> Dict:
        """Retrieve market analysis data and model outputs"""
        try:
            input_collection = self.db["Market_LLM_Input"]
            input_data = list(input_collection.find({}, {"content": 1, "agent": 1}))
            
            # Sample market model output based on your provided structure
            market_analysis = {
                "swot_analysis": {
                    "strengths": ["Strong brand reputation", "Diverse product range"],
                    "weaknesses": ["Weak online presence", "Dependence on third-party suppliers"],
                    "opportunities": ["Expansion into emerging markets", "Increasing demand for eco-friendly products"],
                    "threats": ["Intense competition", "Changing regulatory environment"]
                },
                "competitive_positioning": {
                    "market_share": "12%",
                    "key_differentiators": ["Innovative product features", "Excellent customer service"],
                    "customer_segments": ["Eco-conscious consumers", "Tech-savvy millennials"]
                },
                "market_analysis": {
                    "industry_trends": ["Rising interest in sustainable products", "Growth in smart home technology"],
                    "consumer_behaviors": ["Increased online shopping", "Preference for high-quality goods"],
                    "market_growth": "5% annual increase in demand for electrical appliances"
                },
                "recommendations": {
                    "strategic_moves": ["Increase digital marketing efforts", "Form strategic partnerships with eco-friendly brands"],
                    "product_development": ["Invest in smart technology", "Enhance eco-friendly product lines"]
                }
            }
            
            return {
                "input_data": input_data,
                "analysis_results": [market_analysis]
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {"input_data": [], "analysis_results": []}
    
    def get_revenue_data(self) -> Dict:
        """Retrieve revenue analysis data and model outputs"""
        try:
            input_collection = self.db["Revenue_LLM_Input"]
            input_data = list(input_collection.find({}, {"content": 1, "agent": 1}))
            
            # Sample revenue model output based on your provided structure
            revenue_analysis = {
                "revenue_forecast": "$1,500,000",
                "confidence_level": "High",
                "key_factors": {
                    "historical_growth": "High Positive",
                    "market_trend": "Moderate Positive",
                    "economic_conditions": "Moderate Negative",
                    "consumer_preferences_shifts": "High Positive",
                    "seasonality": "High Positive"
                },
                "analysis": {
                    "insights": "The revenue trend indicates promising growth driven by increasing demand in both corporate and home office furniture segments. Historical data shows strong sales performance in key months like June and November.",
                    "recommendation": "To maximize revenue potential, it's recommended to focus marketing efforts on the top-performing regions and products during peak seasons."
                },
                "monthly_forecast_next_year": {
                    "january": "$100,000",
                    "february": "$110,000",
                    "march": "$120,000",
                    "april": "$130,000",
                    "may": "$140,000",
                    "june": "$200,000",
                    "july": "$150,000",
                    "august": "$130,000",
                    "september": "$120,000",
                    "october": "$140,000",
                    "november": "$200,000",
                    "december": "$150,000"
                }
            }
            
            return {
                "input_data": input_data,
                "analysis_results": [revenue_analysis]
            }
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
            return {"input_data": [], "analysis_results": []}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")
