from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Gold Calculator backend is running!"}

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    """
    Calculate how many grams of gold you could buy with a given amount of TRY
    on a specific date. Date must be in dd/mm/yyyy format.
    """

    try:
        # Parse the input date
        dt = datetime.strptime(date, "%d/%m/%Y")

        # 1. Gold price in USD per ounce (Gold Futures)
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(
            start=dt.strftime("%Y-%m-%d"),
            end=(dt + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        if gold_data.empty:
            raise HTTPException(status_code=404, detail="No gold data for this date")
        gold_usd_per_oz = gold_data["Close"].iloc[0]

        # 2. USD/TRY exchange rate
        usdtry = yf.Ticker("USDTRY=X")
        usdtry_data = usdtry.history(
            start=dt.strftime("%Y-%m-%d"),
            end=(dt + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        if usdtry_data.empty:
            raise HTTPException(status_code=404, detail="No USD/TRY data for this date")
        usdtry_rate = usdtry_data["Close"].iloc[0]

        # 3. Convert to TRY per gram
        price_per_gram = (gold_usd_per_oz / 31.1035) * usdtry_rate
        grams = amount_try / price_per_gram

        return {
            "date": date,
            "grams": grams,
            "price_per_gram": price_per_gram
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
