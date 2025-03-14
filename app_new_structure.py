import streamlit as st

# Rename the sidebar page title
st.set_page_config(page_title="How It Works")

# Manually set the display name in sidebar
st.sidebar.title("How It Works")

# Configure the page layout with the desired title
st.set_page_config(page_title="How It Works", page_icon="📊", layout="wide")

st.markdown("""# 📈 The Future of Trading: AI-Powered Market Forecasting  

**By Group 3: Josh, Felipe, Sam, Maria, and Edwin**  

---

### **Can Machine Learning Predict the Stock Market?**  

For centuries, the stock market has been a battleground of intuition, strategy, and high-stakes decision-making. Investors pore over balance sheets, earnings reports, and technical charts in search of an edge. But in an era of rapid technological advancement, a new force is entering the trading arena: **artificial intelligence**.  

Enter **Stock Market Live Analysis**, an innovative **AI-powered forecasting model** designed by a team of data scientists—**Josh, Felipe, Sam, Maria, and Edwin**—who have set out to answer a fundamental question:  

> *Can machine learning provide a reliable trading signal for investors—predicting whether they should buy or sell a stock the next day?*  

Using a combination of **historical market data, financial statements, and advanced predictive modeling**, our application provides real-time insights into major stocks like **Apple (AAPL), Microsoft (MSFT), Google (GOOG), Amazon (AMZN), Nvidia (NVDA), Meta (META), and Tesla (TSLA)**.  

---

### **How It Works**  

At the heart of this system is a machine learning model powered by **XGBoost**, trained on historical stock price movements and key financial indicators such as:  

✅ **Price-to-Earnings (P/E) Ratio** – A crucial measure of market valuation  
✅ **50-Day Simple Moving Average (SMA)** – A trend-following indicator  
✅ **Closing Prices & Market Capitalization** – The lifeblood of trading strategies  

The model takes in **real-time data from the SimFin API**, applies **automated ETL transformations**, and delivers a **Buy or Sell** signal—helping traders make data-driven investment decisions.  

---

### **Bringing AI to Your Portfolio**  

This isn’t about replacing human investors—it’s about **enhancing decision-making with data**.  

Through our **interactive Go Live page**, users can:  
📊 Select a stock and retrieve live & historical market data  
📈 View AI-powered predictions for the next trading day  
📉 Receive a **Buy or Sell signal** based on machine learning forecasts  

Whether you’re a seasoned trader or a newcomer navigating the market’s volatility, **Stock Market Live Analysis** gives you a data-driven **edge** in making smarter financial decisions.  

Welcome to the future of investing.  

🚀 *Explore the platform now and let AI guide your next move!*  
""")

