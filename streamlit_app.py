import streamlit as st
import requests
import json
from gtts import gTTS
import os
from sentence_transformers import SentenceTransformer, util
from typing import List

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Dummy sample documents (in real case, load from FAISS or DB)
docs = [
    "TSMC beat earnings by 4% due to strong AI chip demand.",
    "Samsung missed earnings by 2% as memory chip prices declined.",
    "Analysts expect Asian tech stocks to remain strong despite volatility."
]

# Streamlit UI setup
st.set_page_config(page_title="Finance Assistant", page_icon="📈")
st.title("🧠 Multi-Agent Market Brief Generator")

ticker = st.text_input("Enter Stock Ticker (e.g. TSM, AAPL, MSFT)", value="TSM")

if st.button("📊 Get Market Brief"):
    with st.spinner("Fetching and summarizing market data..."):
        try:
            # --- API Agent Logic ---
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
            res = requests.get(url).json()
            quote = res['quoteResponse']['result'][0]
            stock_data = {
                "ticker": ticker,
                "shortName": quote.get("shortName"),
                "currentPrice": quote.get("regularMarketPrice"),
                "marketCap": quote.get("marketCap"),
                "fiftyTwoWeekHigh": quote.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": quote.get("fiftyTwoWeekLow"),
                "previousClose": quote.get("regularMarketPreviousClose"),
                "open": quote.get("regularMarketOpen"),
            }

            # --- Retrieval Agent Logic ---
            query = f"{ticker} earnings"
            query_embedding = embedder.encode(query, convert_to_tensor=True)
            doc_embeddings = embedder.encode(docs, convert_to_tensor=True)
            hits = util.semantic_search(query_embedding, doc_embeddings, top_k=2)
            top_docs = [docs[hit['corpus_id']] for hit in hits[0]]

            # --- Language Agent Logic ---
            summary = (
                f"Good morning! {stock_data['shortName']} ({ticker}) is currently trading at "
                f"${stock_data['currentPrice']}, with a market cap of ${stock_data['marketCap']:,}. "
                f"52-week range: ${stock_data['fiftyTwoWeekLow']} - ${stock_data['fiftyTwoWeekHigh']}.\n\n"
                f"Here's what you need to know: {top_docs[0]} Also, {top_docs[1]}"
            )

            # --- Voice Agent (TTS) ---
            tts = gTTS(summary)
            audio_file = f"summary_audio_{ticker}.mp3"
            tts.save(audio_file)

            # Display result
            st.subheader("📝 Summary")
            st.write(summary)

            st.subheader("🔊 Voice Output")
            with open(audio_file, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
