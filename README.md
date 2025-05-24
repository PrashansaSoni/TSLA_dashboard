
# 📊 TSLA Stock Data Visualization App

This Streamlit app provides interactive visualization and analysis of Tesla (TSLA) stock data. It includes candlestick charts, directional markers, support/resistance levels, and an AI-powered chatbot to answer questions about the data.

🚀 Features

   * 📈 Candlestick Charts: Visualize OHLCV data with TradingView-style charts.

   * 🧭 Directional Markers: Identify buy/sell points using marker symbols.

   * 📊 Support/Resistance Levels: Highlight key price levels.

   * 💬 AI Chatbot (Gemini API): Ask questions about TSLA stock data and get AI-powered insights.

   * ⏮️ Moving Animation video : TradingView-style bar replay animation.


## How to run

1.  **Clone the repository:**
      ```bash

     git clone https://github.com/PrashansaSoni/TSLA_dashboard.git
     cd TSLA_dashboard
     ```
     

2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
    ```


3. **Start the FastAPI backend:**
   ```bash
   cd chatbot/backend
   uvicorn main:app --reload
   ```

4. **Run the Streamlit frontend:**
   ```bash
   cd chatbot
   streamlit run app.py
   ```

