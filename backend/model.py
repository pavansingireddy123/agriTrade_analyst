# model.py
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX

def load_and_preprocess_data():
    """Load and preprocess both datasets with enhanced type handling"""
    # Load datasets
    df_districts = pd.read_csv("./datasets/DISTRTICTS_DATASET final.csv")
    df_crop = pd.read_csv("./datasets/Cropcost.csv")

    # Process districts data
    df_districts = df_districts.rename(columns={
        'District Name': 'District',
        'Commodity': 'Crop',
        'Modal Price (Rs./Quintal)': 'Price',
        'Price Date': 'Date',
        'qn_per_acre': 'qn_per_acre'
    })

    # Convert date and handle errors
    df_districts['Date'] = pd.to_datetime(
        df_districts['Date'], 
        format='%d-%m-%Y', 
        errors='coerce'
    )
    
    # Clean numeric columns
    df_districts['Price'] = pd.to_numeric(
        df_districts['Price'].astype(str).str.replace(',', ''),
        errors='coerce'
    )
    
    df_districts['qn_per_acre'] = pd.to_numeric(
        df_districts['qn_per_acre'].astype(str).str.replace(',', ''),
        errors='coerce'
    )

    # Clean and standardize crop names
    df_districts['Crop'] = (
        df_districts['Crop']
        .str.lower()
        .str.replace(r'\(.*\)', '', regex=True)
        .str.replace('common', '', regex=False)
        .str.strip()
    )

    # Drop invalid rows
    df_districts = df_districts.dropna(subset=['Date', 'Price', 'qn_per_acre'])

    # Process crop cost data
    df_crop['Crop_Type'] = (
        df_crop['Crop_Type']
        .str.lower()
        .str.strip()
    )
    df_crop['Season'] = (
        df_crop['Season']
        .str.strip()
        .str.title()
    )
    
    # Clean expenditure data
    df_crop['Total_Expenditure'] = pd.to_numeric(
        df_crop['Total_Expenditure'].astype(str).str.replace(',', ''),
        errors='coerce'
    )
    
    return df_districts, df_crop

# Load preprocessed data
df_districts, df_crop = load_and_preprocess_data()

def calculate_financials(district, crop, season, acres, start_date):
    """Calculate financial projections with enhanced error handling"""
    try:
        # Validate input types
        acres = float(acres)
        crop = crop.lower().strip()
        district = district.strip()
        season = season.strip().title()

        # --- Income Calculation ---
        district_data = df_districts[
            (df_districts['District'] == district) &
            (df_districts['Crop'] == crop)
        ].copy()

        if district_data.empty:
            raise ValueError(f"No data for {crop} in {district}")

        # Prepare time series data
        district_data = district_data.sort_values('Date').set_index('Date')
        
        # Handle possible NaN values in price
        if district_data['Price'].isnull().all():
            raise ValueError(f"Insufficient price data for {crop} in {district}")

        # SARIMAX model configuration
        model = SARIMAX(
            district_data['Price'].interpolate(),
            order=(1, 1, 1),
            seasonal_order=(0, 0, 0, 0),
            enforce_stationarity=False
        )
        results = model.fit(disp=False)

        # Generate forecast
        forecast = results.get_forecast(steps=30)
        avg_price = float(forecast.predicted_mean.mean())

        # Get quintals per acre with validation
        qn_per_acre = district_data['qn_per_acre'].iloc[0]
        if pd.isnull(qn_per_acre) or qn_per_acre <= 0:
            qn_per_acre = 10.0  # Default fallback value

        total_income = avg_price * acres * float(qn_per_acre)

        # --- Expense Calculation ---
        crop_data = df_crop[
            (df_crop['Crop_Type'] == crop) &
            (df_crop['Season'] == season)
        ]

        if crop_data.empty:
            raise ValueError(f"No {season} cost data for {crop}")

        expense_per_acre = float(crop_data['Total_Expenditure'].iloc[0])
        total_expense = expense_per_acre * acres

        return {
            "totalIncome": round(total_income, 2),
            "totalExpense": round(total_expense, 2),
            "balance": round(total_income - total_expense, 2),
            "pricePerQuintal": round(avg_price, 2),
            "quintalsPerAcre": round(qn_per_acre, 2)
        }

    except Exception as e:
        raise ValueError(f"Calculation error: {str(e)}") from e