# 📈 Financial API Data Pipeline & Visualization

## 🌟 Project Overview

This project implements a complete **Financial Time Series Analysis Pipeline** that automates the collection, processing, and visualization of historical stock market data to perform technical trend analysis.

It is a showcase of proficiency in **API integration**, **Pandas data manipulation**, **Feature Engineering**, and generating complex, informative **Dual-Axis Visualizations**.

### Key Technical Skills

* **API Integration & Pipeline:** Engineered a data pipeline integrating the **Alpha Vantage API** for automated ingestion of daily stock time-series data (OHLCV).
* **Data Transformation:** Utilized **Pandas** for cleaning, time-series indexing, and ensuring data type integrity.
* **Feature Engineering:** Calculated the **20-day Simple Moving Average (SMA)** as a core technical feature for trend identification.
* **Advanced Visualization:** Developed a custom **Matplotlib dual-axis chart** to simultaneously visualize Price/SMA trend and Trading Volume.

---

## 🛠️ How to Run the Project

### Prerequisites

1.  **Python 3.x**
2.  **Alpha Vantage API Key** (Free sign-up required)

### Setup & Execution

1.  **Install Dependencies:** Open your terminal in the project directory and run:
    ```bash
    pip install pandas matplotlib requests
    ```
2.  **Configure API Key:** Open `stock_analyzer.py` and replace the placeholder API key with your actual Alpha Vantage key.
3.  **Run the Script:**
    ```bash
    python stock_analyzer.py
    ```

The script will fetch data for **AAPL**, process it, and display a visualization of the last 180 trading days.

---

## 📊 Analysis and Conclusion

The visualization provides a powerful overview for assessing short-term market health.

### Visualization Summary:

* **Primary Axis (Blue/Red Lines):** Closing Price vs. the 20-day SMA, indicating the core price trend.
* **Secondary Axis (Grey Bars):** Trading Volume, showing market activity and conviction.

### Data-Driven Insight:

The analysis shows that during the visualized period, the price consistently remained **above the 20-day SMA**. This indicates a **strong, short-term bullish uptrend** was in effect, with the SMA acting as a reliable dynamic support level. High-volume bars often correlated with significant price movements, confirming strong conviction in those trading days.

****

---

## 💡 Future Enhancements

* Add support for other technical indicators (e.g., RSI, MACD).
* Convert the visualization to an interactive library (Plotly or Bokeh).
* Implement command-line arguments to dynamically select the stock symbol and SMA period.
