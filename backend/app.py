from fastapi import FastAPI, HTTPException
import investpy

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Gold Calculator backend is running!"}

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    try:
        data = investpy.get_currency_cross_historical_data(
            currency_cross='GAU/TRY',
            from_date=date,
            to_date=date
        )
        if data.empty:
            raise HTTPException(status_code=404, detail="No gold price data for this date")

        price_per_gram = data['Close'].iloc[0]
        grams = amount_try / price_per_gram
        return {
            "date": date,
            "grams": grams,
            "price_per_gram": price_per_gram
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
