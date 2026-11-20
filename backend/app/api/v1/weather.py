
from fastapi import APIRouter, HTTPException, Query

from backend.app.services import weather_analytics as analytics

router = APIRouter(
    prefix="/weather",
    tags=["Historical Weather Analytics"]
)


@router.get("/overview")
def get_overview():
    try:
        return {"success": True, "data": analytics.overview()}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/locations")
def get_locations():
    try:
        return {"success": True, "data": analytics.location_list()}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/monthly")
def get_monthly(location: str | None = Query(default=None)):
    try:
        return {
            "success": True,
            "data": analytics.monthly_analysis(location)
        }
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/yearly")
def get_yearly(location: str | None = Query(default=None)):
    try:
        return {
            "success": True,
            "data": analytics.yearly_analysis(location)
        }
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/comparison")
def get_comparison():
    try:
        return {
            "success": True,
            "data": analytics.location_comparison()
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/features")
def get_features():
    try:
        return {
            "success": True,
            "data": analytics.feature_analysis()
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
