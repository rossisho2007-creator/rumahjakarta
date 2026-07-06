import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json

st.set_page_config(page_title="RumahJakarta Pro", layout="wide", page_icon="🏠")

# ============ CUSTOM CSS ============
st.markdown("""
<style>
.big-number { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
.prediction-box { padding: 2rem; border-radius: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.region-card { padding: 1rem; border-radius: 0.5rem; background: #f8f9fa; cursor: pointer; transition: 0.3s; }
.region-card:hover { background: #e9ecef; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/raw/jakarta_data.csv')
        return df
    except:
        return None

df = load_data()

# ============ CURRENCY ============
EXCHANGE = {
    'IDR (Rupiah)': {'rate': 1, 'symbol': 'Rp', 'format': 'M'},
    'USD': {'rate': 0.000064, 'symbol': '$', 'format': ',.0f'},
    'SGD': {'rate': 0.000086, 'symbol': 'S$', 'format': ',.0f'},
    'EUR': {'rate': 0.000059, 'symbol': '€', 'format': ',.0f'},
    'AUD': {'rate': 0.000099, 'symbol': 'A$', 'format': ',.0f'},
}

st.sidebar.header("💱 Settings")
currency = st.sidebar.selectbox("Currency", list(EXCHANGE.keys()))

def fmt_price(million_idr):
    info = EXCHANGE[currency]
    if currency == 'IDR (Rupiah)':
        return f"{info['symbol']} {million_idr:,.0f}M"
    else:
        converted = million_idr * 1e6 * info['rate']
        if converted > 1e6:
            return f"{info['symbol']} {converted/1e6:.2f}M"
        return f"{info['symbol']} {converted:,.0f}"

# ============ MAIN APP ============
st.title("🏠 RumahJakarta Pro")
st.markdown("*Interactive Jakarta Property Analysis*")

if df is None:
    st.error("Please run gen_data.py first!")
    st.stop()

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "🏠 Property Finder", "📊 Analytics"])

# ============ TAB 1: INTERACTIVE MAP ============
with tab1:
    st.header("🗺️ Jakarta Housing Heatmap")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("Map Filters")
        prop_filter = st.selectbox("Property Type", ["All", "House", "Apartment"])
        metric = st.selectbox("Color By", ["Price/m²", "Total Price", "Distance to Mall"])
        
        st.subheader("Click a Region")
        selected_region = st.selectbox("Or select:", 
            ["All"] + sorted(df['region'].unique().tolist()))
    
    with col1:
        # Filter data
        map_df = df.copy()
        if prop_filter != "All":
            map_df = map_df[map_df['property_type'] == prop_filter.lower()]
        if selected_region != "All":
            map_df = map_df[map_df['region'] == selected_region]
        
        # Determine color metric
        if metric == "Price/m²":
            color_col = 'price_per_m2'
            color_label = 'Price per m² (Million IDR)'
            map_df['display_color'] = map_df['price_per_m2'] / 1_000_000
        elif metric == "Total Price":
            color_col = 'price_million_idr'
            color_label = 'Price (Million IDR)'
            map_df['display_color'] = map_df['price_million_idr']
        else:
            color_col = 'dist_nearest_mall_km'
            color_label = 'Distance to Mall (km)'
            map_df['display_color'] = map_df['dist_nearest_mall_km']
        
        # Create interactive map
        fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lon',
            color='display_color',
            size='price_million_idr',
            size_max=20,
            hover_name='name',
            hover_data={
                'region': True,
                'property_type': True,
                'price_million_idr': ':.0f',
                'land_m2': True,
                'building_m2': True,
                'bedrooms': True,
                'floors': True,
                'dist_airport_km': ':.1f',
                'dist_nearest_mall_km': ':.2f',
                'lat': False,
                'lon': False,
                'display_color': False
            },
            color_continuous_scale='RdYlGn_r' if 'mall' in metric.lower() else 'Viridis',
            zoom=10,
            center={'lat': -6.2000, 'lon': 106.8166},
            mapbox_style='carto-positron',
            title=f'Jakarta Properties - {metric}'
        )
        
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=30, b=0),
            coloraxis_colorbar=dict(title=color_label)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Click handling via selectbox
        if selected_region != "All":
            st.subheader(f"📊 {selected_region} Statistics")
            region_df = df[df['region'] == selected_region]
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Avg Price", fmt_price(region_df['price_million_idr'].mean()))
            with c2:
                st.metric("Avg Price/m²", fmt_price(region_df['price_per_m2'].mean() / 1_000_000))
            with c3:
                st.metric("Properties", len(region_df))
            with c4:
                st.metric("Avg Size", f"{region_df['building_m2'].mean():.0f} m²")

# ============ TAB 2: PROPERTY FINDER ============
with tab2:
    st.header("🏠 Find Your Property")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Location")
        find_region = st.selectbox("Region", sorted(df['region'].unique()))
        find_type = st.selectbox("Type", ["house", "apartment"])
        find_mall_dist = st.slider("Max distance to mall (km)", 0.5, 20.0, 5.0)
    
    with col2:
        st.subheader("Size")
        find_land_min = st.number_input("Min land (m²)", 0, 500, 60)
        find_land_max = st.number_input("Max land (m²)", 0, 500, 500)
        find_building = st.number_input("Min building (m²)", 0, 500, 36)
        find_floors = st.selectbox("Floors", [1, 2, 3, 4])
    
    with col3:
        st.subheader("Budget")
        find_budget = st.number_input("Max budget (Million IDR)", 100, 50000, 5000)
        find_bedrooms = st.number_input("Bedrooms", 1, 8, 2)
    
    if st.button("🔍 Search Properties", use_container_width=True):
        results = df[
            (df['region'] == find_region) &
            (df['property_type'] == find_type) &
            (df['dist_nearest_mall_km'] <= find_mall_dist) &
            (df['price_million_idr'] <= find_budget) &
            (df['bedrooms'] >= find_bedrooms) &
            (df['floors'] >= find_floors)
        ]
        
        if find_type == 'house':
            results = results[
                (results['land_m2'] >= find_land_min) &
                (results['land_m2'] <= find_land_max)
            ]
        else:
            results = results[results['building_m2'] >= find_building]
        
        st.success(f"Found {len(results)} matching properties!")
        
        if len(results) > 0:
            # Show results on map
            fig = px.scatter_mapbox(
                results,
                lat='lat', lon='lon',
                hover_name='name',
                hover_data=['price_million_idr', 'land_m2', 'building_m2', 'bedrooms'],
                color='price_million_idr',
                size='building_m2',
                zoom=11,
                mapbox_style='carto-positron'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            display_cols = ['name', 'area', 'land_m2', 'building_m2', 'floors', 
                          'bedrooms', 'bathrooms', 'price_million_idr', 'dist_nearest_mall_km']
            st.dataframe(results[display_cols].head(20), use_container_width=True)
            
            # Future projection
            st.subheader("📈 Value Projection")
            years = st.slider("Years to project", 1, 20, 5, key='proj_years')
            
            avg_price = results['price_million_idr'].mean()
            growth = st.slider("Annual growth (%)", 1, 15, 8, key='growth')
            
            future = [avg_price * (1 + growth/100)**y for y in range(years+1)]
            proj_df = pd.DataFrame({
                'Year': range(2026, 2027+years),
                'Value (Million IDR)': future
            })
            
            fig = px.line(proj_df, x='Year', y='Value (Million IDR)', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Current Avg", fmt_price(avg_price))
            st.metric(f"In {years} years", fmt_price(future[-1]),
                     f"+{((future[-1]/avg_price-1)*100):.0f}%")

# ============ TAB 3: ANALYTICS ============
with tab3:
    st.header("📊 Market Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price by Region")
        region_stats = df.groupby('region').agg(
            avg_price=('price_million_idr', 'mean'),
            count=('id', 'count')
        ).reset_index()
        
        fig = px.bar(region_stats, x='region', y='avg_price', 
                    color='region', title='Average Price by Region')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("House vs Apartment")
        type_stats = df.groupby('property_type').agg(
            avg_price=('price_million_idr', 'mean'),
            avg_size=('building_m2', 'mean')
        ).reset_index()
        
        fig = px.pie(type_stats, values='avg_price', names='property_type',
                    title='Price Distribution: House vs Apartment')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Price Factors Analysis")
    st.info("""
    **Factors affecting Jakarta property prices (in order of importance):**
    1. **Location (Region)** - Central Jakarta commands highest prices
    2. **Property Type** - Houses generally more expensive than apartments
    3. **Land Size** - Key factor for houses
    4. **Building Size** - Key factor for apartments
    5. **Distance to Malls** - Closer properties fetch 15-25% premium
    6. **Housing Name** - Regal/English names add 10-18% premium
    7. **Floors** - Multi-story houses valued higher
    8. **Airport Proximity** - 15-30km range is optimal
    
    *Note: Local neighborhood factors (including religious buildings) 
    are incorporated but not explicitly displayed.*
    """)

st.markdown("---")
st.caption("RumahJakarta Pro | Interactive Jakarta Property Analysis")