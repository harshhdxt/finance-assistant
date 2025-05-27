import streamlit as st
import requests
import os

# UI config
st.set_page_config(page_title="Finance Assistant", page_icon="📈")
st.title("📢 Morning Market Brief")

# Input for ticker
ticker = st.text_input("Enter a stock ticker (e.g., TSM, AAPL, MSFT)", value="TSM")

# Button to get summary
if st.button("🎯 Get Market Brief"):
    with st.spinner("Fetching market data and generating brief..."):
        try:
            # Call orchestrator API
            response = requests.get(f"http://localhost:8004/market-brief/?ticker={ticker}")
            data = response.json()

            # Display summary
            if "final_summary" in data:
                st.subheader("🧾 Market Summary")
                st.write(data["final_summary"])

                # Play audio
                if "audio_file" in data and os.path.exists(data["audio_file"]):
                    st.subheader("🔊 Listen to Brief")
                    with open(data["audio_file"], "rb") as audio:
                        st.audio(audio.read(), format="audio/mp3")
                else:
                    st.warning("⚠️ Audio file not found.")
            else:
                st.error("❌ No summary found in response.")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
