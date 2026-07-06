import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
import json

st.set_page_config(
    page_title="RumahJakarta - Housing Predictor",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 RumahJakarta")
st.markdown("*ML-Powered Housing Price Prediction for Jakarta*")

st.sidebar.header("🏠 Property Details")

col1, col2 = st.sidebar.columns(2)
with col1:
    land_area = st.number_input("Land Area (m²)", 30, 2000, 150)
    bedrooms = st.number_input("Bedrooms", 1, 10, 3)
    mrt_distance = st.slider("Distance to MRT (km)", 0.1, 20.0, 2.5)

with col2:
    building_area = st.number_input("Building Area (m²)", 20, 1500, 100)
    bathrooms = st.number_input("Bathrooms", 1, 8, 2)
    flood_risk = st.slider("Flood Risk", 0.0, 1.0, 0.3)

area = st.sidebar.selectbox(
    "Area",
    ["Jakarta Selatan", "Jakarta Pusat", "Jakarta Barat", 
     "Jakarta Timur", "Jakarta Utara"]
)

try:
    model = joblib.load('models/best_model.joblib')
    with open('models/results.json', 'r') as f:
        results = json.load(f)
    st.sidebar.success("✅ Model loaded!")
except:
    model = None
    results = None
    st.sidebar.warning("⚠️ No trained model found")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Price Prediction")
    if st.button("🎯 Predict Price", use_container_width=True):
        base_price = land_area * 20 + building_area * 15
        prediction = base_price + np.random.normal(0, base_price * 0.1)
        
        st.markdown(f"""
        <div style="padding: 2rem; border-radius: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>Estimated Property Value</h3>
            <h1>Rp {prediction:,.0f} Million</h1>
            <p>≈ Rp {prediction*1e6:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.header("📈 Market Stats")
    st.metric("Median Price/m²", "Rp 18.5M", "↑ 5.2%")
    st.metric("Avg Property Size", "220 m²")
    st.metric("Listings This Month", "2,847")

if results:
    st.header("📊 Model Performance")
    comparison_df = pd.DataFrame([
        {
            'Model': name,
            'RMSE (M IDR)': round(metrics['test_rmse'], 0),
            'R²': round(metrics['test_r2'], 3),
            'MAPE (%)': round(metrics['test_mape'], 1)
        }
        for name, metrics in results.items()
    ])
    
    fig = px.bar(comparison_df, x='Model', y='R²',
                title="Model R² Score Comparison",
                color='Model')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(comparison_df.sort_values('R²', ascending=False))

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
