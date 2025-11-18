from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime, timedelta
import os

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("index.html")

def get_closest_price(ticker, dt):
    """Find closest available price by searching backwards indefinitely until found."""
    days_back = 0
    while True:
        check_date = dt - timedelta(days=days_back)
        data = ticker.history(
            start=check_date.strftime("%Y-%m-%d"),
            end=(check_date + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        if not data.empty:
            return data["Close"].iloc[0], check_date.strftime("%d/%m/%Y")
        days_back += 1
        if days_back > 365*5:  # safety stop after 5 years back
            raise HTTPException(status_code=404, detail="No data found in last 5 years")

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    try:
        dt = datetime.strptime(date, "%d/%m/%Y")

        # Gold price (USD/oz)
        gold_price, gold_date = get_closest_price(yf.Ticker("GC=F"), dt)

        # USD/TRY exchange
        usdtry_price, usdtry_date = get_closest_price(yf.Ticker("USDTRY=X"), dt)

        # Convert to TRY/g
        price_per_gram = (gold_price / 31.1035) * usdtry_price

        # Apply +3% markup to price
        price_per_gram_with_markup = price_per_gram * 1.03

        grams = amount_try / price_per_gram_with_markup

        return {
            "date": date,
            "grams": grams,
            "price_per_gram": price_per_gram_with_markup
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
