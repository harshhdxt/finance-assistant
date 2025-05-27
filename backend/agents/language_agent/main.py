from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import dotenv_values
from pathlib import Path
from .schemas import LanguageRequest

# Load OpenRouter key
env_path = Path(__file__).parent / "open.env"
env_vars = dotenv_values(env_path)
OPENAI_API_KEY = env_vars.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(f"OPENAI_API_KEY not found in {env_path}. Please check the file content.")

# Initialize FastAPI app
app = FastAPI()

# 🔄 Use OpenRouter as backend for ChatOpenAI
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="openai/gpt-3.5-turbo",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.4
)


@app.get("/ping")
def ping():
    return {"message": "Language Agent is working!"}

@app.post("/generate-summary/")
def generate_summary(payload: LanguageRequest):
    try:
        stock_data = payload.stock_data
        news = payload.earnings_news.top_news
        context = payload.retrieved_context.results

        news_text = "\n".join([f"- {item.title}" for item in news]) if news else "No headlines available."
        context_text = "\n".join(context) if context else "No extra context available."

        prompt = f"""
You are a financial assistant for a portfolio manager. Based on the following data, generate a short spoken-style market brief (2–3 sentences):

📊 Stock Info:
{stock_data}

📰 Earnings Headlines:
{news_text}

📚 Context:
{context_text}
"""

        print("🔎 Prompt to LLM:")
        print(prompt)

        messages = [
            SystemMessage(content="You are a professional financial assistant that produces short, clear morning market briefs."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        print("✅ LLM response:", response.content)

        return {"summary": response.content}

    except Exception as e:
        print("❌ Error in /generate-summary/:", str(e))
        return {"error": str(e)}
