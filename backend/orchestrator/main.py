from fastapi import FastAPI, Query
import requests
from gtts import gTTS
import os

app = FastAPI()

# Agent endpoints
API_AGENT_URL = "http://localhost:8001/stock-data/"
SCRAPING_AGENT_URL = "http://localhost:8002/earnings-news/"
RETRIEVAL_AGENT_URL = "http://localhost:8003/retrieve/"
LANGUAGE_AGENT_URL = "http://localhost:8005/generate-summary/"

@app.get("/ping")
def ping():
    return {"message": "Orchestrator is live!"}

@app.get("/market-brief/")
def market_brief(ticker: str = Query("TSM")):
    result = {}

    # 1. Get Stock Info
    try:
        stock_data = requests.get(API_AGENT_URL, params={"ticker": ticker}).json()
        result["stock_data"] = stock_data
    except Exception as e:
        result["stock_data"] = {"error": str(e)}

    # 2. Get Earnings News
    try:
        earnings_news = requests.get(SCRAPING_AGENT_URL, params={"ticker": ticker}).json()
        result["earnings_news"] = earnings_news
    except Exception as e:
        result["earnings_news"] = {"error": str(e)}

    # 3. Get Retrieved Context
    try:
        query = f"{ticker} earnings"
        retrieved_context = requests.get(RETRIEVAL_AGENT_URL, params={"query": query, "top_k": 2}).json()
        result["retrieved_context"] = retrieved_context
    except Exception as e:
        result["retrieved_context"] = {"error": str(e)}

    # 4. Get Summary from Language Agent + Generate Audio
    try:
        summary_response = requests.post(LANGUAGE_AGENT_URL, json=result)
        print("🧠 Language Agent raw response:", summary_response.text)
        summary_json = summary_response.json()
        summary_text = summary_json.get("summary", summary_json)

        result["final_summary"] = summary_text

        # 🎤 Generate audio file from summary
        tts = gTTS(summary_text)
        audio_filename = f"summary_audio_{ticker}.mp3"
        tts.save(audio_filename)
        result["audio_file"] = audio_filename

    except Exception as e:
        result["final_summary"] = f"Summary generation failed: {str(e)}"

    return result
