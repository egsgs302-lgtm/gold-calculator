from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime, timedelta
import os

app = FastAPI()

# Serve the frontend
@app.get("/")
def home():
    return FileResponse("index.html")


def get_closest_price(ticker, dt):
    """Find closest available price within 7 days back."""
    for i in range(7):
        check_date = dt - timedelta(days=i)
        data = ticker.history(
            start=check_date.strftime("%Y-%m-%d"),
            end=(check_date + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        if not data.empty:
            return data["Close"].iloc[0], check_date.strftime("%d/%m/%Y")
    raise HTTPException(status_code=404, detail="No data found within 7 days")


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

        # Apply +3% markup
        grams = (amount_try * 1.03) / price_per_gram

        # Build 10-year history (Jan 1 each year)
        history = []
        for year in range(dt.year - 10, dt.year + 1):
            jan1 = datetime(year, 1, 1)
            g_price, g_date = get_closest_price(yf.Ticker("GC=F"), jan1)
            u_price, u_date = get_closest_price(yf.Ticker("USDTRY=X"), jan1)
            ppg = (g_price / 31.1035) * u_price
            history.append({"year": year, "date": g_date, "price_per_gram": ppg})

        return {
            "date": date,
            "grams": grams,
            "price_per_gram": price_per_gram,
            "history": history
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
