from fastapi import FastAPI, Query
from pydantic import BaseModel
from pathlib import Path
import uvicorn

from predict import predict_next_days

app = FastAPI(title="Energy Forecasting API", version="1.0.0")

DEVICE_LIST = ["tgbt", "ac", "compressor"]

class PredictionRequest(BaseModel):
    device: str
    horizon_days: int = Query(7, ge=1, le=30)

@app.post("/predict", summary="Get energy forecast with maintenance check", tags=["Forecast"])
def predict_energy(req: PredictionRequest):
    device = req.device.lower()
    horizon = req.horizon_days

    if device not in DEVICE_LIST:
        return {"error": f"Device '{device}' not supported. Choose from {DEVICE_LIST}"}

    try:
        forecast, alerts = predict_next_days(device, days=horizon)
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

    forecast_dict = {str(date): kwh for date, kwh, _ in forecast}

    return {
        "device": device,
        "horizon_days": horizon,
        "forecast_kwh": forecast_dict,
        "alerts": alerts if alerts else ["✅ No anomalies detected."]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
