import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap, MarkerCluster, Fullscreen
from branca.colormap import LinearColormap
import json

st.set_page_config(
    page_title="RumahJakarta | Property Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ STYLING ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    * {font-family: 'Plus Jakarta Sans', sans-serif;}
    #MainMenu, footer, .stDeployButton {display: none;}
    .main .block-container {padding-top: 1.5rem;}
    
    .brand {display: flex; align-items: center; gap: 0.75rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f0f0f0; margin-bottom: 1.5rem;}
    .brand-icon {width: 36px; height: 36px; background: #1a1a1a; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700;}
    .brand-text {font-size: 1.3rem; font-weight: 600; color: #1a1a1a; letter-spacing: -0.5px;}
    
    .stat-box {padding: 1.25rem; background: #fafafa; border-radius: 8px;}
    .stat-label {font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px;}
    .stat-value {font-size: 1.4rem; font-weight: 600; color: #1a1a1a; margin-top: 0.25rem;}
    
    .prediction-card {background: linear-gradient(135deg, #1a1a1a 0%, #333 100%); padding: 2rem; border-radius: 12px; color: white;}
    .prediction-card .price {font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;}
    .prediction-card .label {font-size: 0.8rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 1px;}
    
    .property-row {display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #f5f5f5;}
    .property-row:hover {background: #fafafa;}
    
    .stButton > button {background: #1a1a1a; color: white; border: none; border-radius: 6px; padding: 0.6rem 1.5rem; font-weight: 500; transition: all 0.2s;}
    .stButton > button:hover {background: #333; border: none; transform: translateY(-1px);}
    
    .stTabs [data-baseweb="tab-list"] {gap: 2rem; border-bottom: 1px solid #f0f0f0;}
    .stTabs [data-baseweb="tab"] {font-size: 0.85rem; font-weight: 500; color: #888; padding: 0.5rem 0;}
    .stTabs [aria-selected="true"] {color: #1a1a1a; border-bottom: 2px solid #1a1a1a;}
</style>
""", unsafe_allow_html=True)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    try:
        return pd.read_csv('data/raw/jakarta_data.csv')
    except:
        import subprocess
        subprocess.run(['python', 'src/data/gen_data.py'], capture_output=True)
        return pd.read_csv('data/raw/jakarta_data.csv')

df = load_data()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Theme")
    theme = st.selectbox("", ["Light", "Dark"], label_visibility="collapsed")
    st.caption("Currency")
    currency = st.selectbox("", ["IDR (Rp)", "USD ($)", "SGD (S$)"], label_visibility="collapsed")

if theme == "Dark":
    st.markdown("""
    <style>
        .stApp {background-color: #141414;}
        .brand-text {color: #fff;}
        .brand {border-bottom-color: #333;}
        .stat-box {background: #1e1e1e !important;}
        .stat-label {color: #888 !important;}
        .stat-value {color: #fff !important;}
        .brand-icon {background: #fff; color: #1a1a1a;}
        .property-row {border-bottom-color: #333;}
        .property-row:hover {background: #1e1e1e;}
        .stTabs [data-baseweb="tab"] {color: #888;}
        .stTabs [aria-selected="true"] {color: #fff; border-bottom-color: #fff;}
        .stTabs [data-baseweb="tab-list"] {border-bottom-color: #333;}
    </style>
    """, unsafe_allow_html=True)

# Currency
RATES = {'IDR (Rp)': 1, 'USD ($)': 0.000064, 'SGD (S$)': 0.000086}
SYMBOLS = {'IDR (Rp)': 'Rp', 'USD ($)': '$', 'SGD (S$)': 'S$'}

def fmt(million_idr):
    rate = RATES[currency]
    sym = SYMBOLS[currency]
    if currency == 'IDR (Rp)':
        if million_idr >= 1000:
            return f"{sym} {million_idr/1000:.1f}B"
        return f"{sym} {million_idr:,.0f}M"
    else:
        val = million_idr * 1e6 * rate
        if val > 1e6:
            return f"{sym} {val/1e6:.2f}M"
        elif val > 1000:
            return f"{sym} {val/1000:,.0f}K"
        return f"{sym} {val:,.0f}"

# ============ HEADER ============
st.markdown("""
<div class="brand">
    <div class="brand-icon">RJ</div>
    <div class="brand-text">RumahJakarta</div>
</div>
""", unsafe_allow_html=True)

# ============ STATS ROW ============
avg_price = df['price_million_idr'].mean()
median_price = df['price_million_idr'].median()
total_props = len(df)
regions_count = df['region'].nunique()

st.markdown(f"""
<div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
    <div class="stat-box" style="flex:1;">
        <div class="stat-label">Total Listings</div>
        <div class="stat-value">{total_props:,}</div>
    </div>
    <div class="stat-box" style="flex:1;">
        <div class="stat-label">Median Price</div>
        <div class="stat-value">{fmt(median_price)}</div>
    </div>
    <div class="stat-box" style="flex:1;">
        <div class="stat-label">Average Price</div>
        <div class="stat-value">{fmt(avg_price)}</div>
    </div>
    <div class="stat-box" style="flex:1;">
        <div class="stat-label">Regions</div>
        <div class="stat-value">{regions_count}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Price Predictor", "🗺️ Interactive Map", "📋 Browse Listings", "📊 Analytics"])

# ============================================
# TAB 1: PRICE PREDICTOR
# ============================================
with tab1:
    st.markdown("### Property Price Predictor")
    st.caption("Enter details to get an AI-powered price estimate with future projections")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        region = st.selectbox("Region", sorted(df['region'].unique()))
        prop_type = st.selectbox("Property Type", ["House", "Apartment"])
        area = st.selectbox("Area/Neighborhood", sorted(df[df['region'] == region]['area'].unique()))
        
        cA, cB = st.columns(2)
        with cA:
            land = st.number_input("Land Area (m²)", 30, 2000, 150)
            beds = st.number_input("Bedrooms", 1, 10, 3)
            floors = st.number_input("Floors", 1, 5, 2)
        with cB:
            building = st.number_input("Building Area (m²)", 20, 1500, 100)
            baths = st.number_input("Bathrooms", 1, 8, 2)
            mall_dist = st.number_input("Distance to Mall (km)", 0.1, 20.0, 2.0)
        
        airport_dist = st.slider("Distance to Airport (km)", 5, 60, 25)
        name_type = st.radio("Housing Name Style", ["Regal/English", "Indonesian/Local"], horizontal=True)
    
    with col2:
        if st.button("Calculate Price Estimate", use_container_width=True):
            with st.spinner("Analyzing property data..."):
                region_avg = df[df['region'] == region]['price_per_m2'].median()
                
                if prop_type == "House":
                    base = land * region_avg
                    construction = building * floors * 5_000_000
                else:
                    base = building * region_avg * 1.2
                    construction = 0
                
                name_mult = 1.15 if name_type == "Regal/English" else 1.0
                mall_mult = 1.15 if mall_dist < 1 else (1.05 if mall_dist < 3 else 0.95)
                airport_mult = 1.10 if 15 <= airport_dist <= 30 else 0.95
                
                predicted = (base + construction) * name_mult * mall_mult * airport_mult
                predicted_m = predicted / 1_000_000
                
                st.markdown(f"""
                <div class="prediction-card">
                    <div class="label">Estimated Property Value</div>
                    <div class="price">{fmt(predicted_m)}</div>
                    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">≈ Rp {predicted_m:,.0f}M (base currency)</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Price Breakdown")
                st.dataframe(pd.DataFrame([
                    {"Factor": "Base Property Value", "Impact": "—", "Amount": fmt(base/1_000_000)},
                    {"Factor": "Construction Cost", "Impact": "—", "Amount": fmt(construction/1_000_000)},
                    {"Factor": "Name Style Premium", "Impact": f"+{(name_mult-1)*100:.0f}%" if name_mult > 1 else "—", "Amount": fmt(predicted_m - (base+construction)/1_000_000)},
                    {"Factor": "Mall Proximity", "Impact": f"+{(mall_mult-1)*100:.0f}%" if mall_mult > 1 else f"-{(1-mall_mult)*100:.0f}%", "Amount": fmt(predicted_m * abs(1 - 1/mall_mult))},
                    {"Factor": "Airport Distance", "Impact": f"+{(airport_mult-1)*100:.0f}%" if airport_mult > 1 else f"-{(1-airport_mult)*100:.0f}%", "Amount": fmt(predicted_m * abs(1 - 1/airport_mult))},
                ]), use_container_width=True, hide_index=True)
                
                # Future Projections
                st.markdown("---")
                st.markdown("#### 📈 Future Value Projection")
                
                pc1, pc2 = st.columns(2)
                with pc1:
                    years = st.slider("Years to project", 1, 20, 10, key="years_proj")
                with pc2:
                    growth = st.slider("Annual growth rate (%)", 1, 15, 8, key="growth_proj")
                
                future = [predicted_m * (1 + growth/100)**y for y in range(years + 1)]
                year_labels = list(range(2026, 2026 + years + 1))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=year_labels, y=future,
                    mode='lines+markers',
                    line=dict(color='#1a1a1a', width=2),
                    marker=dict(size=8, color='#1a1a1a'),
                    fill='tozeroy',
                    fillcolor='rgba(26,26,26,0.1)'
                ))
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0),
                                xaxis_title="Year", yaxis_title=f"Value ({SYMBOLS[currency]})",
                                template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                
                sc1, sc2, sc3 = st.columns(3)
                with sc1:
                    st.metric("Current Value", fmt(predicted_m))
                with sc2:
                    st.metric(f"Value in {years} years", fmt(future[-1]))
                with sc3:
                    st.metric("Total Growth", f"+{((future[-1]/predicted_m - 1) * 100):.0f}%")

# ============================================
# TAB 2: INTERACTIVE MAP
# ============================================
with tab2:
    st.markdown("### 🗺️ Jakarta Property Map")
    st.caption("Interactive heatmap • Zoom, click markers for details • Fullscreen available")
    
    mc1, mc2, mc3 = st.columns([1, 1, 2])
    
    with mc1:
        map_type = st.selectbox("Property Type", ["All", "House", "Apartment"], key="maptype")
    with mc2:
        map_region = st.selectbox("Region", ["All Jakarta"] + sorted(df['region'].unique().tolist()), key="mapregion")
    with mc3:
        color_by = st.selectbox("Color By", ["Price", "Price/m²", "Building Size", "Mall Distance"], key="colorby")
    
    # Map settings
    with st.expander("Map Settings", expanded=False):
        set1, set2, set3 = st.columns(3)
        with set1:
            show_heat = st.checkbox("Show Heatmap Layer", value=True)
        with set2:
            cluster_markers = st.checkbox("Cluster Markers", value=True)
        with set3:
            opacity_val = st.slider("Marker Opacity", 0.3, 1.0, 0.7)
    
    # Filter
    map_df = df.copy()
    if map_type != "All":
        map_df = map_df[map_df['property_type'] == map_type.lower()]
    if map_region != "All Jakarta":
        map_df = map_df[map_df['region'] == map_region]
    if len(map_df) > 500:
        map_df = map_df.sample(500, random_state=42)
        st.caption(f"Displaying 500 of {len(df)} properties for performance")
    
    # Build map
    m = folium.Map(location=[-6.2000, 106.8166], zoom_start=11, tiles='CartoDB positron', control_scale=True)
    Fullscreen(position='topright', title='Fullscreen', title_cancel='Exit').add_to(m)
    
    # Color column
    if color_by == "Price":
        ccol, clabel = 'price_million_idr', 'Price (M IDR)'
    elif color_by == "Price/m²":
        ccol, clabel = 'price_per_m2', 'Price/m²'
    elif color_by == "Building Size":
        ccol, clabel = 'building_m2', 'Building (m²)'
    else:
        ccol, clabel = 'dist_nearest_mall_km', 'Dist to Mall (km)'
    
    vmin, vmax = map_df[ccol].min(), map_df[ccol].max()
    
    if "Mall" in color_by:
        colors = ['red', 'orange', 'yellow', 'green']
    else:
        colors = ['green', 'yellow', 'orange', 'red']
    
    colormap = LinearColormap(colors=colors, vmin=vmin, vmax=vmax, caption=clabel)
    m.add_child(colormap)
    
    # Add markers
    if cluster_markers:
        marker_group = MarkerCluster().add_to(m)
    else:
        marker_group = folium.FeatureGroup(name="Properties").add_to(m)
    
    for _, row in map_df.iterrows():
        color = colormap(row[ccol])
        
        popup_html = f"""
        <div style="font-family:sans-serif;font-size:13px;width:230px;">
            <b style="font-size:14px;">{row['name']}</b><br>
            <span style="color:#666;">{row['area']}, {row['region']}</span><br>
            <b style="font-size:16px;">{fmt(row['price_million_idr'])}</b><br>
            <hr style="margin:5px 0;">
            📐 {row['land_m2']}m² land · 🏗️ {row['building_m2']}m² build<br>
            🛏️ {row['bedrooms']} bed · 🛁 {row['bathrooms']} bath · 🏢 {row['floors']} floors<br>
            🛍️ {row['dist_nearest_mall_km']:.1f}km to mall · ✈️ {row['dist_airport_km']:.0f}km to airport
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=7,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=opacity_val,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{row['name']} - {fmt(row['price_million_idr'])}"
        ).add_to(marker_group)
    
    # Heatmap
    if show_heat:
        heat_data = [[row['lat'], row['lon'], row['price_million_idr']] for _, row in map_df.iterrows()]
        HeatMap(heat_data, radius=15, blur=10, max_zoom=13, name="Heatmap").add_to(m)
    
    folium.LayerControl().add_to(m)
    folium_static(m, width=1100, height=550)

# ============================================
# TAB 3: BROWSE LISTINGS
# ============================================
with tab3:
    st.markdown("### Browse Properties")
    
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        search = st.text_input("Search", placeholder="Name or area...", label_visibility="collapsed")
    with f2:
        f_type = st.selectbox("Type", ["All", "House", "Apartment"], key="ftype", label_visibility="collapsed")
    with f3:
        f_region = st.selectbox("Region", ["All"] + sorted(df['region'].unique().tolist()), key="fregion", label_visibility="collapsed")
    with f4:
        f_sort = st.selectbox("Sort", ["Price: High-Low", "Price: Low-High"], key="fsort", label_visibility="collapsed")
    
    display = df.copy()
    if search:
        display = display[display['name'].str.contains(search, case=False) | display['area'].str.contains(search, case=False)]
    if f_type != "All":
        display = display[display['property_type'] == f_type.lower()]
    if f_region != "All":
        display = display[display['region'] == f_region]
    display = display.sort_values('price_million_idr', ascending=("Low" in f_sort))
    
    st.caption(f"{len(display)} properties found")
    
    for _, row in display.head(20).iterrows():
        st.markdown(f"""
        <div class="property-row">
            <div>
                <strong>{row['name']}</strong><br>
                <span style="color:#888;font-size:0.85rem;">{row['area']}, {row['region']} · {row['property_type'].title()} · 
                {row['land_m2']}m² land · {row['building_m2']}m² build · {row['bedrooms']} bed · {row['bathrooms']} bath · 
                {row['floors']} floors · {row['dist_nearest_mall_km']:.1f}km to mall</span>
            </div>
            <div style="text-align:right;font-weight:600;font-size:1.1rem;">{fmt(row['price_million_idr'])}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# TAB 4: ANALYTICS
# ============================================
with tab4:
    st.markdown("### Market Analytics")
    
    ac1, ac2 = st.columns(2)
    
    with ac1:
        st.caption("Price Distribution by Region")
        fig = px.box(df, x='region', y='price_million_idr', color='region',
                    color_discrete_sequence=['#1a1a1a','#333','#555','#777','#999'])
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), showlegend=False)
        fig.update_xaxes(title=""); fig.update_yaxes(title="Price (Million IDR)")
        st.plotly_chart(fig, use_container_width=True)
    
    with ac2:
        st.caption("House vs Apartment by Region")
        type_avg = df.groupby(['region','property_type'])['price_million_idr'].mean().reset_index()
        fig = px.bar(type_avg, x='region', y='price_million_idr', color='property_type',
                    barmode='group', color_discrete_sequence=['#1a1a1a','#888'])
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation='h',y=1.05))
        fig.update_xaxes(title=""); fig.update_yaxes(title="Avg Price (M IDR)")
        st.plotly_chart(fig, use_container_width=True)
    
    ac3, ac4 = st.columns(2)
    
    with ac3:
        st.caption("Price vs Mall Distance")
        fig = px.scatter(df.sample(200), x='dist_nearest_mall_km', y='price_million_idr',
                        color='region', size='building_m2',
                        color_discrete_sequence=['#1a1a1a','#333','#555','#777','#999'])
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), showlegend=False)
        fig.update_xaxes(title="Distance to Mall (km)"); fig.update_yaxes(title="Price (M IDR)")
        st.plotly_chart(fig, use_container_width=True)
    
    with ac4:
        st.caption("Building Size vs Price with Trend")
        fig = px.scatter(df.sample(200), x='building_m2', y='price_million_idr',
                        color='property_type', trendline='ols',
                        color_discrete_sequence=['#1a1a1a','#888'])
        fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation='h',y=1.05))
        fig.update_xaxes(title="Building Size (m²)"); fig.update_yaxes(title="Price (M IDR)")
        st.plotly_chart(fig, use_container_width=True)

# ============ FOOTER ============
st.markdown("---")
st.caption("© 2024 RumahJakarta · Property Intelligence Platform")