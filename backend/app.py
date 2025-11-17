from fastapi import FastAPI
import investpy

app = FastAPI()

@app.get("/gold")
def get_gold_price(date: str, amount_try: float):
    """
    date must be in dd/mm/yyyy format (e.g., '15/11/2025')
    """
    data = investpy.get_currency_cross_historical_data(
        currency_cross='GAU/TRY',
        from_date=date,
        to_date=date
    )
    price_per_gram = data['Close'].iloc[0]
    grams = amount_try / price_per_gram
    return {
        "date": date,
        "grams": grams,
        "price_per_gram": price_per_gram
    }
