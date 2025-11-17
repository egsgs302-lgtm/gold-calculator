from fastapi import FastAPI, HTTPException
import investpy
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
        from_date = dt.strftime("%d/%m/%Y")
        to_date = (dt + timedelta(days=1)).strftime("%d/%m/%Y")

        # 1. Get gold price in USD per ounce (XAU/USD)
        gold_data = investpy.get_currency_cross_historical_data(
            currency_cross='XAU/USD',
            from_date=from_date,
            to_date=to_date
        )
        if gold_data.empty:
            raise HTTPException(status_code=404, detail="No gold price data for this date")
        gold_usd_per_oz = gold_data['Close'].iloc[0]

        # 2. Get USD/TRY exchange rate
        usdtry_data = investpy.get_currency_cross_historical_data(
            currency_cross='USD/TRY',
            from_date=from_date,
            to_date=to_date
        )
        if usdtry_data.empty:
            raise HTTPException(status_code=404, detail="No USD/TRY data for this date")
        usdtry = usdtry_data['Close'].iloc[0]

        # 3. Convert to TRY per gram
        price_per_gram = (gold_usd_per_oz / 31.1035) * usdtry

        # 4. Calculate grams of gold for the given amount
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
