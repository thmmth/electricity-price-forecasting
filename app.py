import streamlit as st
from tabs import tab_models, tab_pun, tab_commodities, tab_terna, tab_weather

st.set_page_config(page_title="Energy Dashboard", layout="wide")

st.title("📊 Energy Dashboard")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 ML Models", 
    "💡 PUN Index GME", 
    "💰 Commodities", 
    "🔌 Terna", 
    "🌦️ Weather"
])

with tab1:
    tab_models.render()

with tab2:
    tab_pun.render()

with tab3:
    tab_commodities.render()

with tab4:
    tab_terna.render()

with tab5:
    tab_weather.render()
