from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yfinance as yf
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/")
def home():
    return FileResponse("index.html")

def get_closest_common_date(dt):
    """Find the closest date backwards where both gold and USD/TRY have data."""
    days_back = 0
    gold_ticker = yf.Ticker("GC=F")
    usdtry_ticker = yf.Ticker("USDTRY=X")

    while True:
        check_date = dt - timedelta(days=days_back)

        gold_data = gold_ticker.history(
            start=check_date.strftime("%Y-%m-%d"),
            end=(check_date + timedelta(days=1)).strftime("%Y-%m-%d")
        )
        usdtry_data = usdtry_ticker.history(
            start=check_date.strftime("%Y-%m-%d"),
            end=(check_date + timedelta(days=1)).strftime("%Y-%m-%d")
        )

        if not gold_data.empty and not usdtry_data.empty:
            gold_price = gold_data["Close"].iloc[0]
            usdtry_price = usdtry_data["Close"].iloc[0]
            return gold_price, usdtry_price, check_date.strftime("%d/%m/%Y")

        days_back += 1
        if days_back > 365*50:  # safety stop
            raise HTTPException(status_code=404, detail="No common data found in last 50 years")

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    try:
        dt = datetime.strptime(date, "%d/%m/%Y")

        gold_price, usdtry_price, found_date = get_closest_common_date(dt)

        # Convert to TRY/g
        price_per_gram = (gold_price / 31.1035) * usdtry_price

        # Apply +3% markup
        price_per_gram_with_markup = price_per_gram * 1.03

        grams = amount_try / price_per_gram_with_markup

        return {
            "date": found_date,
            "grams": round(grams, 2),
            "price_per_gram": price_per_gram_with_markup
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
