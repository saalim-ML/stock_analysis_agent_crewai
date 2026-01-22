# stock_analysis_agent_crewai
This project implements a **multi-agent AI system** using **CrewAI** to perform **real-time stock analysis and trading decisions**.   It uses multiple AI agents with different roles to analyze stock market data and recommend whether to **Buy, Sell, or Hold** a stock.

The system integrates **live stock data from Yahoo Finance**, **internet search tools**, and **LLMs** to simulate a collaborative financial analysis workflow.

---

## 📌 Key Concepts Covered

- Multi-Agent Systems
- Agent Roles & Goals
- Tool-Using Agents
- Real-time Data Integration
- CrewAI Framework
- Sequential Task Processing
- LLM-powered Financial Analysis

---

## 🧠 Technologies Used

- Python
- CrewAI
- Groq LLM (`llama-3.3-70b-versatile`)
- Yahoo Finance (`yfinance`)
- Tavily Search Tool
- dotenv (environment variables)

---

## 🤖 Agents in the System

### 1️⃣ Financial Market Analyst
**Role:**  
Analyzes live stock data and market trends.

**Tools Used:**
- Live Stock Information Tool
- Internet Search Tool

**Responsibilities:**
- Fetch current price
- Analyze daily change & volume
- Summarize stock performance

---
https://stockanalysisagentcrewai.streamlit.app/
