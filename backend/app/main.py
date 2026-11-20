from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.app.pv_engine.solar_forecast import generate_solar_forecast
from backend.app.api.v1.weather import router as weather_router
app = FastAPI(
    title="Solar AI Forecasting System",
    description="Location-aware solar power forecasting for Bangladesh",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    weather_router,
    prefix="/api/v1"
)

class ForecastRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    panel_area: float = Field(default=30, gt=0)
    panel_efficiency: float = Field(default=0.20, gt=0, le=1)
    panel_tilt: float = Field(default=23, ge=0, le=90)
    panel_azimuth: float = Field(default=180, ge=0, le=360)
    inverter_capacity: float = Field(default=5, gt=0)
    inverter_efficiency: float = Field(default=0.97, gt=0, le=1)
    forecast_hours: int = Field(default=48, ge=24, le=48)


@app.get("/")
def home():
    return {
        "message": "Solar AI Forecasting System is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/v1/forecast")
def forecast(request: ForecastRequest):
    try:
        result = generate_solar_forecast(
            latitude=request.latitude,
            longitude=request.longitude,
            panel_area=request.panel_area,
            panel_efficiency=request.panel_efficiency,
            panel_tilt=request.panel_tilt,
            panel_azimuth=request.panel_azimuth,
            inverter_capacity=request.inverter_capacity,
            inverter_efficiency=request.inverter_efficiency,
            forecast_hours=request.forecast_hours
        )

        return {
            "success": True,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "installation": request.model_dump(),
            "forecast": result
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))