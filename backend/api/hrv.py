from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models import HRVReading, User
from backend.hrv_calculator import HRVCalculator

router = APIRouter()
hrv_calc = HRVCalculator()

class RRIntervalsInput(BaseModel):
    """Input model for raw RR intervals"""
    rr_intervals: List[float] = Field(..., description="List of R-R intervals in milliseconds")
    recorded_at: datetime
    sleep_duration: Optional[float] = None
    sleep_quality: Optional[float] = None

class HRVReadingResponse(BaseModel):
    """Response model for HRV reading"""
    id: int
    user_id: int
    recorded_at: datetime

    # Time domain
    mean_rri: Optional[float]
    mean_hr: Optional[float]
    sdnn: Optional[float]
    rmssd: Optional[float]
    pnn50: Optional[float]

    # Frequency domain
    vlf_power: Optional[float]
    lf_power: Optional[float]
    hf_power: Optional[float]
    total_power: Optional[float]
    lf_hf_ratio: Optional[float]

    # Quality
    recording_duration: Optional[float]
    artifact_percentage: Optional[float]

    class Config:
        from_attributes = True

@router.post("/{user_id}/readings", response_model=HRVReadingResponse, status_code=status.HTTP_201_CREATED)
def create_hrv_reading(
    user_id: int,
    data: RRIntervalsInput,
    db: Session = Depends(get_db)
):
    """
    Calculate and store HRV metrics from raw RR intervals.

    Args:
        user_id: User ID
        data: RR intervals and metadata

    Returns:
        Calculated HRV metrics
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check data quality
    quality = hrv_calc.check_data_quality(data.rr_intervals)
    if not quality['is_valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data quality: {', '.join(quality['issues'])}"
        )

    # Calculate all metrics
    try:
        metrics = hrv_calc.calculate_all_metrics(data.rr_intervals)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating HRV metrics: {str(e)}"
        )

    # Create reading
    reading = HRVReading(
        user_id=user_id,
        recorded_at=data.recorded_at,
        mean_rri=metrics['mean_rri'],
        mean_hr=metrics['mean_hr'],
        sdnn=metrics['sdnn'],
        rmssd=metrics['rmssd'],
        pnn50=metrics['pnn50'],
        vlf_power=metrics['vlf_power'],
        lf_power=metrics['lf_power'],
        hf_power=metrics['hf_power'],
        total_power=metrics['total_power'],
        lf_hf_ratio=metrics['lf_hf_ratio'],
        lf_nu=metrics['lf_nu'],
        hf_nu=metrics['hf_nu'],
        sleep_duration=data.sleep_duration,
        sleep_quality=data.sleep_quality,
        recording_duration=len(data.rr_intervals) / 60.0,  # Approximate minutes
        artifact_percentage=quality['artifact_percentage']
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return reading

@router.get("/{user_id}/readings", response_model=List[HRVReadingResponse])
def get_hrv_readings(
    user_id: int,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get recent HRV readings for a user.

    Args:
        user_id: User ID
        limit: Maximum number of readings to return

    Returns:
        List of HRV readings
    """
    readings = db.query(HRVReading).filter(
        HRVReading.user_id == user_id
    ).order_by(
        HRVReading.recorded_at.desc()
    ).limit(limit).all()

    return readings

@router.get("/{user_id}/readings/{reading_id}", response_model=HRVReadingResponse)
def get_hrv_reading(
    user_id: int,
    reading_id: int,
    db: Session = Depends(get_db)
):
    """Get specific HRV reading"""
    reading = db.query(HRVReading).filter(
        HRVReading.id == reading_id,
        HRVReading.user_id == user_id
    ).first()

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading not found"
        )

    return reading
