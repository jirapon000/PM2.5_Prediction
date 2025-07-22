# 🌫️ PM2.5 Prediction and Air Quality Monitoring Dashboard

This project offers **real-time monitoring** and **predictive insights** into air quality conditions using the **Air Quality Index (AQI)**.  
It focuses on pollutant concentrations such as **PM2.5, PM10, SO₂, NO₂, CO**, and **O₃**, helping users make informed decisions and take preventive actions based on both current and forecasted data.

## 🚀 Key Features

- **📡 Real-Time Monitoring**  
  Track up-to-date air quality levels across major pollutants, including:
  - PM2.5 (fine particulate matter)
  - PM10 (inhalable particles)
  - SO₂ (sulfur dioxide)
  - NO₂ (nitrogen dioxide)
  - CO (carbon monoxide)
  - O₃ (ozone)

- **🤖 Predictive Modeling**  
  Forecast future pollutant levels using machine learning models trained on historical air quality datasets.

- **📊 Interactive Dashboard**  
  A visually intuitive dashboard that presents pollutant data with color-coded indicators and trend visualizations for easy interpretation.

- **🛡️ Protective Guidelines**  
  Recommendations and best practices for protecting yourself from harmful pollutants, with a focus on PM2.5 and other common air toxins.

- **🔮 Air Quality Forecasting**  
  View short-term and medium-term air quality forecasts to plan daily activities and reduce exposure risk.

## 🧪 Dataset & API

This project does **not** rely on a static dataset. Instead, it uses **real-time air quality data** obtained through a live **API** integration.

The application automatically pulls the latest pollutant measurements, including:

- PM2.5 (fine particulate matter)
- PM10 (inhalable particles)
- SO₂ (sulfur dioxide)
- NO₂ (nitrogen dioxide)
- CO (carbon monoxide)
- O₃ (ozone)

These real-time values are fetched directly when the application is run, allowing users to view up-to-date air quality information without the need to manually download or update data.

> 🔗 *Note: Ensure a stable internet connection to allow successful API calls during runtime.*

## 🌐 Website Overview

The web application consists of three main pages, each providing a unique view into air quality monitoring and prediction:

### 🏠 Home Page
- Displays **real-time pollutant data** updated live via API
- Highlights the **top 5 most polluted areas in Bangkok** based on current pollutant levels
- Provides a quick overview of key pollutant concentrations including PM2.5, PM10, SO₂, NO₂, CO, and O₃

### 📈 Predictive Page
- Focuses on **PM2.5 forecasting only**
- Uses a machine learning model trained on historical data to **predict future PM2.5 levels**
- Helps users plan activities and reduce exposure during high-risk periods

### 🧪 Simulation Page
- An interactive environment where users can **adjust variables** such as:
  - Temperature
  - PM10
  - SO₂, NO₂, CO, and O₃
- Simulates how changes in these variables affect **PM2.5 levels**
- Visualizes which factors have the greatest impact on air quality

This structure allows users to monitor current conditions, anticipate future risks, and explore how environmental variables interact with fine particulate matter (PM2.5).

## 📁 How to Run the App

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/PM2.5_Prediction.git

2. **Run the application**
   ```bash
   python app.py

3. **Open your browser and go to:**
   ```bash
   [python app.py](http://localhost:5000)
