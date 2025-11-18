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
    """Search backwards until data is found (no limit)."""
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
        if days_back > 365*50:  # safety stop after 50 years
            raise HTTPException(status_code=404, detail="No data found in last 50 years")

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    try:
        dt = datetime.strptime(date, "%d/%m/%Y")

        # Gold price (USD/oz)
        gold_price, gold_found_date = get_closest_price(yf.Ticker("GC=F"), dt)

        # USD/TRY exchange
        usdtry_price, usdtry_found_date = get_closest_price(yf.Ticker("USDTRY=X"), dt)

        # Convert to TRY/g
        price_per_gram = (gold_price / 31.1035) * usdtry_price

        # Apply +3% markup to price
        price_per_gram_with_markup = price_per_gram * 1.03

        grams = amount_try / price_per_gram_with_markup

        return {
            "requested_date": date,
            "gold_found_date": gold_found_date,
            "usdtry_found_date": usdtry_found_date,
            "grams": round(grams, 2),
            "price_per_gram": price_per_gram_with_markup
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
