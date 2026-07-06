# 🏠 RumahJakarta - Jakarta Housing Price Predictor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered housing & apartment price prediction for Jakarta, Indonesia. Features interactive maps, multi-model ML predictions, and real market data analysis.

## 🎯 Features

- **🗺️ Interactive Jakarta Map** - Clickable regions with heatmap visualization
- **🏠 House & Apartment Support** - Separate pricing models for each
- **🤖 Multi-Model ML** - KNN, XGBoost, Random Forest, Linear Regression
- **📈 Future Projections** - 1-20 year price growth predictions
- **💱 Multi-Currency** - IDR, USD, SGD, EUR, AUD support
- **📍 Real Location Factors**:
  - Distance to Soekarno-Hatta Airport
  - Proximity to major malls (15+ malls mapped)
  - 5 Jakarta regions with verified pricing
  - Housing name analysis (Regal vs Indonesian)
  - Building specifications (floors, land, building size)

## 🗺️ Data Sources
-   Real Jakarta property market data (2024)
-   5 administrative regions with verified pricing
-   15+ major shopping malls with coordinates
-   Soekarno-Hatta International Airport proximity
-   Local neighborhood factors

## 📁 Project Structure

 rumahjakarta/
├── src/
│   ├── data/
│   │   └── gen_data.py          # Data generator
│   └── models/
│       └── model.py              # ML training
├── app/
│   └── app.py                    # Streamlit dashboard
├── data/
│   ├── raw/                      # Generated datasets
│   └── processed/                # Processed data
├── models/                       # Trained models
├── requirements.txt
└── README.md

## 🛠️ Technology Stack
-   Frontend: Streamlit, Plotly
-   ML: Scikit-learn, XGBoost
-   Data: Pandas, NumPy
-   Visualization: Plotly Express, Mapbox

## 📄 License
-   MIT License - see LICENSE file

## 🤝 Contributing
-   Contributions welcome! Please open an issue or PR.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rumahjakarta.git
cd rumahjakarta

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate data
python src/data/gen_data.py

# Run the app
streamlit run app/app.py

