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
    Get how many grams of gold you could buy with a given amount of TRY
    on a specific date. Date must be in dd/mm/yyyy format.
    """

    try:
        # Parse the input date
        dt = datetime.strptime(date, "%d/%m/%Y")
        from_date = dt.strftime("%d/%m/%Y")
        to_date = (dt + timedelta(days=1)).strftime("%d/%m/%Y")

        # Fetch historical GAU/TRY data for that 2-day range
        data = investpy.get_currency_cross_historical_data(
            currency_cross='GAU/TRY',
            from_date=from_date,
            to_date=to_date
        )

        if data.empty:
            raise HTTPException(status_code=404, detail="No gold price data available for this date")

        # Take the first day's closing price
        price_per_gram = data['Close'].iloc[0]
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
