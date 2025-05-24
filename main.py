
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from streamlit_lightweight_charts import renderLightweightCharts
import requests
from groq import Groq

#Page Configuration
st.set_page_config(page_title="TSLA Dashboard", layout="wide")
st.title("TSLA Dashboard")

# Load Groq API Key
groq_api_key = st.secrets["groq"]["api_key"]
client = Groq(api_key=groq_api_key)

#  Load and Preprocess Data 
@st.cache_data
def load_data():
    df = pd.read_csv("TSLA_data.csv")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['Support'] = df['Support'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    df['Resistance'] = df['Resistance'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    return df

df = load_data()

# Prepare Candlestick Data 
candlestick_data = [
    {
        "time": int(row['timestamp'].timestamp()),
        "open": row['open'],
        "high": row['high'],
        "low": row['low'],
        "close": row['close']
    }
    for _, row in df.iterrows()
]

#  Prepare Markers
markers = []
for _, row in df.iterrows():
    ts = int(row['timestamp'].timestamp())
    direction = row['direction']
    if direction == 'LONG':
        markers.append({"time": ts, "position": "belowBar", "color": "green", "shape": "arrowUp", "text": "LONG"})
    elif direction == 'SHORT':
        markers.append({"time": ts, "position": "aboveBar", "color": "red", "shape": "arrowDown", "text": "SHORT"})
    else:
        markers.append({"time": ts, "position": "inBar", "color": "yellow", "shape": "circle", "text": "NONE"})

# Prepare Support/Resistance Bands
support_bands = []
resistance_bands = []

for _, row in df.iterrows():
    ts = int(row['timestamp'].timestamp())
    if row['Support']:
        support_bands.append({"time": ts, "value": min(row['Support']), "color": "rgba(0, 255, 0, 0.1)"})
        support_bands.append({"time": ts, "value": max(row['Support']), "color": "rgba(0, 255, 0, 0.1)"})
    if row['Resistance']:
        resistance_bands.append({"time": ts, "value": min(row['Resistance']), "color": "rgba(255, 0, 0, 0.1)"})
        resistance_bands.append({"time": ts, "value": max(row['Resistance']), "color": "rgba(255, 0, 0, 0.1)"})

#  Streamlit Tabs 
tabs = st.tabs(["TradingView Lightweight Charts Visualization", "🤖 Chatbot","📊 Moving Animation" ,"📈 Candlestick Chart"])

# ================== Trading view =====================
with tabs[0]:
    from ast import literal_eval
    from streamlit.components.v1 import html

    

    # Convert datetime to Unix timestamp
    df['unix_time'] = df['timestamp'].astype(int) // 10**9

    # Prepare candlestick data
    candlestick_data = df[['unix_time', 'open', 'high', 'low', 'close']].rename(
        columns={'unix_time': 'time'}).to_dict('records')

    # Prepare markers
    markers = []
    for _, row in df.iterrows():
        marker = {
            'time': row['unix_time'],
            'text': row['direction'] if pd.notnull(row['direction']) else 'None'
        }

        if row['direction'] == 'LONG':
            marker.update({
                'position': 'belowBar',
                'shape': 'arrowUp',
                'color': '#00FF00',
                'borderColor': '#006600'
            })
        elif row['direction'] == 'SHORT':
            marker.update({
                'position': 'aboveBar',
                'shape': 'arrowDown',
                'color': '#FF0000',
                'borderColor': '#660000'
            })
        else:
            marker.update({
                'position': 'inBar',
                'shape': 'circle',
                'color': '#FFFF00',
                'borderColor': '#888800'
            })
        markers.append(marker)

    # Prepare support/resistance bands
    def prepare_bands(df, column_name):
        lower = []
        upper = []
        for _, row in df.iterrows():
            if row[column_name]:
                lower_val = min(row[column_name])
                upper_val = max(row[column_name])
                lower.append({'time': row['unix_time'], 'value': lower_val})
                upper.append({'time': row['unix_time'], 'value': upper_val})
        return lower, upper

    support_lower, support_upper = prepare_bands(df, 'Support')
    resistance_lower, resistance_upper = prepare_bands(df, 'Resistance')

    # Chart configuration
    chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            #container {{
                width: 100%;
                height: 600px;
            }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <script>
            const chart = LightweightCharts.createChart(document.getElementById('container'), {{
                layout: {{
                    background: {{ color: '#1E1E1E' }},
                    textColor: '#FFFFFF',
                }},
                grid: {{
                    vertLines: {{ color: '#2B2B43' }},
                    horzLines: {{ color: '#2B2B43' }},
                }},
                timeScale: {{
                    timeVisible: true,
                    secondsVisible: false,
                }},
                width: document.getElementById('container').clientWidth,
                height: 600,
            }});

            // Candlestick series
            const candleSeries = chart.addCandlestickSeries();
            candleSeries.setData({json.dumps(candlestick_data)});
            candleSeries.setMarkers({json.dumps(markers)});

            // Support band (green)
            const supportLowerSeries = chart.addLineSeries({{
                color: 'rgba(0, 255, 0, 0.3)',
                lineWidth: 2,
                title: 'Support Lower',
            }});
            supportLowerSeries.setData({json.dumps(support_lower)});

            const supportUpperSeries = chart.addLineSeries({{
                color: 'rgba(0, 255, 0, 0.3)',
                lineWidth: 2,
                title: 'Support Upper',
            }});
            supportUpperSeries.setData({json.dumps(support_upper)});

            // Resistance band (red)
            const resistanceLowerSeries = chart.addLineSeries({{
                color: 'rgba(255, 0, 0, 0.3)',
                lineWidth: 2,
                title: 'Resistance Lower',
            }});
            resistanceLowerSeries.setData({json.dumps(resistance_lower)});

            const resistanceUpperSeries = chart.addLineSeries({{
                color: 'rgba(255, 0, 0, 0.3)',
                lineWidth: 2,
                title: 'Resistance Upper',
            }});
            resistanceUpperSeries.setData({json.dumps(resistance_upper)});

            // Handle window resize
            window.addEventListener('resize', () => {{
                chart.resize(document.getElementById('container').clientWidth, 600);
            }});
        </script>
    </body>
    </html>
    """

   

    # Display the chart
    html(chart_html, height=600)

    # Data summary
    st.subheader("Data Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Data Points", len(df))
    with col2:
        st.metric("Latest Close Price", f"${df.iloc[-1]['close']:.2f}")

    # Raw data preview
    st.subheader("Raw Data Preview")
    # Replace the existing "Raw Data Preview" section with:

    # Raw data preview with expander
    with st.expander("📁 View Full Raw Data (Click to Expand)"):
        st.dataframe(df.style.format({
            'open': '{:.2f}',
            'high': '{:.2f}',
            'low': '{:.2f}',
            'close': '{:.2f}',
            'volume': '{:.2f}'
        }))

    # Add summary statistics
    st.subheader("Key Statistics")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total LONG Signals", df[df['direction'] == 'LONG'].shape[0])
    with cols[1]:
        st.metric("Total SHORT Signals", df[df['direction'] == 'SHORT'].shape[0])
    with cols[2]:
        st.metric("Total None Signals", df[df['direction'].isna()].shape[0])

#  Chatbot 

with tabs[1]:
    st.title("Agentic  Chatbot")

    API_URL = "http://localhost:8000/chat"
    prompt = st.text_area("Enter your message:")

    if st.button("Send"):
        if prompt.strip():
            with st.spinner("LLM processing the query..."):
                try:
                    res = requests.post(API_URL, json={"message": prompt})
                    if res.status_code == 200:
                        data = res.json()
                        st.markdown("### Response")
                        st.write(data["response"])
                    else:
                        st.error(f"API Error: {res.status_code} - {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt.")

# ================== Moving Animation =================
with tabs[2]:
    st.subheader("Moving Animation")

    speed = st.slider("Select Replay Speed (seconds per candle)", 0.1, 2.0, 0.5, 0.1)
    start_button = st.button("Start Replay")

    if start_button:
        replay_data = []
        replay_markers = []
        placeholder = st.empty()

        for i in range(len(candlestick_data)):
            replay_data.append(candlestick_data[i])
            if i < len(markers):
                replay_markers.append(markers[i])

            replay_config = [{
                "chart": {
                    "layout": {"background": {"type": "solid", "color": "#ffffff"}, "textColor": "#000"},
                    "width": 1000,
                    "height": 600
                },
                "series": [
                    {
                        "type": "Candlestick",
                        "data": replay_data,
                        "markers": replay_markers,
                        "options": {
                            "upColor": "#26a69a", "downColor": "#ef5350",
                            "borderVisible": False, "wickUpColor": "#26a69a", "wickDownColor": "#ef5350"
                        }
                    }
                ]
            }]
            placeholder.empty()
            with placeholder.container():
                renderLightweightCharts(replay_config, key=f"replay_{i}")
            time.sleep(speed)

 

# Candlestick

with tabs[3]:
    st.subheader("Candlestick Chart with Markers and Bands")

    chart_config = [{
            "chart": {
                "layout": {"background": {"type": "solid", "color": "#ffffff"}, "textColor": "#000"},
                "width": 1000,
                "height": 600
                
            },
            "series": [
                {
                    "type": "Candlestick",
                    "data": candlestick_data,
                    "markers": markers,
                    "options": {
                        "upColor": "#26a69a", "downColor": "#ef5350",
                        "borderVisible": True, "wickUpColor": "#26a69a", "wickDownColor": "#ef5350"
                    }
                },
                {
                    "type": "Line",
                    "data": support_bands,
                    "options": {"color": "green", "lineWidth": 1, "lineStyle": 1}
                },
                {
                    "type": "Line",
                    "data": resistance_bands,
                    "options": {"color": "red", "lineWidth": 1, "lineStyle": 1}
                }
            ]
        }]

    renderLightweightCharts(chart_config, key="candlestick_chart")

   
   