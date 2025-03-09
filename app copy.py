import streamlit as st

# Configure the page layout
st.set_page_config(page_title="Trading System Overview", layout="wide")

# Title and introduction
st.title("📊 AI-Powered Stock Trading System")
st.markdown("""
### Welcome to our trading system!
This system leverages **Machine Learning** and **Financial Data** from SimFin to provide **real-time stock market analysis and predictions**.

#### 🔍 Core Features:
- **Live & Historical Stock Data** 📈  
- **Real-time Market Analysis** 🔄  
- **AI-Powered Predictions** 🤖  
- **Buy/Sell Trading Signals** 💹  

#### 👨‍💻 Development Team:
- **Sam & Team**
- Developed as part of a **Data Science & Finance Course**
- Uses **Python, Streamlit, XGBoost, and SimFin API**

---
## **🚀 Ready to Get Started?**
Click on **Go Live** in the sidebar to start analyzing stocks!
""")
