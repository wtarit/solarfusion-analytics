# SolarFusion Analytics

This project extracts raw data from the Huawei SolarFusion dashboard and allow analytics with Python tools.

## Problem

The Huawei SolarFusion dashboard provides limited analytics and doesn't offer easy data export functionality. (Maybe it is possible with an Installer account, I'm not sure)

## Components

### `download_data.py`

- Extracts energy balance data from Huawei SolarFusion dashboard
- Downloads data in JSON format for specified date ranges
- Handles authentication via cookies

### `analytics.ipynb`

- Jupyter notebook for data analysis
- Converts JSON data to pandas DataFrames
- Currently implements visualization of Average Daily Profile of Power Consumed

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Get authentication cookie:**

   - Log into your Huawei SolarFusion dashboard
   - Open browser developer tools
   - Go to Network tab and find any API request
   - Copy the `Cookie` header value

3. **Configure environment:**
   - Create a `.env` file with your cookie:
     ```
     FUSIONSOLAR_COOKIE=your_cookie_value_here
     ```
