import streamlit as st
import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv
from crewai import LLM, Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

st.set_page_config(page_title="AI Stock Analyst", page_icon="📈", layout="wide")

# Env Load
load_dotenv()

# --- CSS for Custom Styling---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LLM Setup ---
try:
    llm = LLM(
        model="groq/llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )
except Exception as e:
    st.error(f"Error connecting to LLM: {e}")
    st.stop()

# --- Tools ---
@tool("Live Stock Information Tool")
def get_stock_price(stock_symbol: str) -> str:
    """Retrieves the latest stock price and relevant info."""
    try:
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        return f"Stock: {stock_symbol}\nPrice: {current_price}\nCurrency: {info.get('currency', 'USD')}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool("Internet Search Tool")
def search_tool(query: str):
    """Searches the internet about a given topic."""
    tavily = TavilySearchResults()
    return tavily.invoke(query)

# --- Helper Function for Graph ---
def get_stock_history(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="6mo")
    return hist, stock.info

# --- Main UI ---
st.title("📈 AI Stock Analyst")
st.markdown("-----------")
st.markdown("Enter a stock symbol to get a comprehensive analysis from AI Agents.")


with st.sidebar:
    st.header("Search Settings")
    
    
    
    market_config = {
        "USA (NASDAQ/NYSE)": {"suffix": "",     "example": "TSLA"},
        "India (NSE)":       {"suffix": ".NS",  "example": "RELIANCE"},
        "India (BSE)":       {"suffix": ".BO",  "example": "TCS"},
        "China (SSE)":       {"suffix": ".SS",  "example": "600519 "}, #(Kweichow Moutai)
        "China (SEHK)":      {"suffix": ".HK",  "example": "0700 "}, #(Tencent)
        "Japan (JPX)":       {"suffix": ".T",   "example": "7203 "} #(Toyota)   
    }
    
    
    market_list = list(market_config.keys())
    selected_market = st.selectbox("Select Market", market_list)

    current_config = market_config[selected_market]
    default_example = current_config["example"]
    market_suffix = current_config["suffix"]

    symbol_input = st.text_input(
        f"Enter Stock Symbol (e.g., {default_example})", 
        value=default_example
    ).upper()
    

    if not symbol_input.endswith(market_suffix):
        stock_input = f"{symbol_input}{market_suffix}"
    else:
        stock_input = symbol_input 

    st.write(f"Searching for: **{stock_input}**") 
    
    analyze_btn = st.button("🚀 Run Analysis")
    st.info("Uses **CrewAI** + **Llama 3** + **Tavily**")

# Main Logic
if analyze_btn:
    try:
        
        with st.spinner(f"Fetching data for {stock_input}..."):
            hist_data, info = get_stock_history(stock_input)
            
            if hist_data.empty:
                st.error("Invalid Stock Symbol or No Data Found!")
            else:
                # Top Metrics Display
                curr_price = info.get('currentPrice') or info.get('regularMarketPrice')
                prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
                if curr_price and prev_close:
                    delta = curr_price - prev_close
                    delta_percent = (delta / prev_close) * 100
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Current Price", f"{curr_price} {info.get('currency', 'USD')}")
                    c2.metric("Change", f"{delta:.2f}", f"{delta_percent:.2f}%")
                    c3.metric("Volume", f"{info.get('volume', 'N/A')}")
                
                # Chart Display
                st.subheader(f"📊 {stock_input} - 6 Month Performance")
                st.line_chart(hist_data['Close'], color="#FF4B4B")

                
                st.divider()
                st.subheader("🤖 AI Agent Analysis")
                
                with st.status("AI Agents are working...", expanded=True) as status:
                    
                    # --- Agents & Tasks Setup ---
                    st.write("🔍 Analyst Agent is gathering data...")
                    analyst_agent = Agent(
                        role="Financial Market Analyst",
                        goal="Analyze stock performance using real-time data.",
                        backstory="Expert financial analyst.",
                        llm=llm,
                        tools=[get_stock_price, search_tool],
                        verbose=True
                    )

                    trader_agent = Agent(
                        role="Strategic Stock Trader",
                        goal="Decide Buy/Sell/Hold based on analysis.",
                        backstory="Experienced trader.",
                        llm=llm,
                        verbose=True
                    )

                    analysis_task = Task(
                        description=f"Analyze the performance of {stock_input}. Focus on today's price and news.",
                        expected_output="Bullet point summary of performance.",
                        agent=analyst_agent
                    )

                    trade_task = Task(
                        description=f"Based on analysis of {stock_input}, give a Buy/Sell/Hold recommendation.",
                        expected_output="Trading recommendation with reasons.",
                        agent=trader_agent,
                        context=[analysis_task]
                    )

                    stock_crew = Crew(
                        agents=[analyst_agent, trader_agent],
                        tasks=[analysis_task, trade_task],
                        process=Process.sequential
                    )

                    # Running the Crew
                    result = stock_crew.kickoff(inputs={"stock": stock_input})
                    status.update(label="Analysis Complete!", state="complete", expanded=False)

                # Final Result Display
                st.success("Analysis Ready!")
                st.markdown("### 📝 Strategic Recommendation")
                st.markdown(result)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    
    st.info("👈 Please enter a stock symbol in the sidebar and click 'Run Analysis'")
