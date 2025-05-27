from fastapi import FastAPI, Query
import yfinance as yf

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "API Agent is up and running!"}

@app.get("/stock-data/")
def get_stock_data(ticker: str = Query(..., description="e.g., TSM, 005930.KQ")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "shortName": info.get("shortName"),
            "currentPrice": info.get("currentPrice"),
            "marketCap": info.get("marketCap"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "previousClose": info.get("previousClose"),
            "open": info.get("open")
        }
    except Exception as e:
        return {"error": str(e)}
