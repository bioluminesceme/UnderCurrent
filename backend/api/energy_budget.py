from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend.models import User, HRVReading, Baseline, EnergyBudget
from backend.baseline_tracker import BaselineTracker
from backend.energy_budget_calculator import EnergyBudgetCalculator

router = APIRouter()
baseline_tracker = BaselineTracker()
energy_budget_calc = EnergyBudgetCalculator()

class BaselineResponse(BaseModel):
    """Response model for baseline"""
    id: int
    calculated_at: datetime
    start_date: datetime
    end_date: datetime
    days_count: int
    mean_ln_rmssd: float
    sd_ln_rmssd: float
    mean_rmssd: float
    mean_hr: Optional[float]
    sd_hr: Optional[float]

    class Config:
        from_attributes = True

class EnergyBudgetResponse(BaseModel):
    """Response model for readiness score"""
    id: int
    date: datetime
    energy_budget: float
    hrv_score: float
    rhr_score: float
    sleep_score: float
    stress_score: float
    hrv_zscore: float
    rhr_zscore: float
    pem_risk_level: str
    consecutive_low_days: int
    activity_recommendation: str

    class Config:
        from_attributes = True

class HRVInterpretation(BaseModel):
    """HRV z-score interpretation"""
    z_score: float
    status: str
    interpretation: str
    color: str

@router.post("/{user_id}/baseline", response_model=BaselineResponse)
def calculate_baseline(user_id: int, db: Session = Depends(get_db)):
    """
    Calculate and save new 28-day baseline for user.

    Args:
        user_id: User ID

    Returns:
        Calculated baseline
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Calculate baseline
    baseline_data = baseline_tracker.calculate_baseline(db, user_id)
    if not baseline_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient data for baseline calculation (need at least 7 days)"
        )

    # Save baseline
    baseline = baseline_tracker.save_baseline(db, user_id, baseline_data)

    return baseline

@router.get("/{user_id}/baseline", response_model=BaselineResponse)
def get_active_baseline(user_id: int, db: Session = Depends(get_db)):
    """
    Get current active baseline for user.

    Args:
        user_id: User ID

    Returns:
        Active baseline
    """
    baseline = baseline_tracker.get_active_baseline(db, user_id)
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active baseline found. Create one first."
        )

    return baseline

@router.post("/{user_id}/readiness/{reading_id}", response_model=EnergyBudgetResponse)
def calculate_energy_budget(
    user_id: int,
    reading_id: int,
    db: Session = Depends(get_db)
):
    """
    Calculate readiness score from HRV reading.

    Args:
        user_id: User ID
        reading_id: HRV reading ID

    Returns:
        Calculated readiness score
    """
    # Get HRV reading
    reading = db.query(HRVReading).filter(
        HRVReading.id == reading_id,
        HRVReading.user_id == user_id
    ).first()

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HRV reading not found"
        )

    # Get active baseline
    baseline = baseline_tracker.get_active_baseline(db, user_id)
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active baseline. Calculate baseline first."
        )

    # Calculate readiness
    readiness_data = energy_budget_calc.calculate_energy_budget(
        db, user_id, reading, baseline
    )

    # Save readiness score
    score = energy_budget_calc.save_energy_budget(
        db, user_id, reading.recorded_at, readiness_data
    )

    return score

@router.get("/{user_id}/readiness", response_model=List[EnergyBudgetResponse])
def get_energy_budgets(
    user_id: int,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get recent readiness scores for user.

    Args:
        user_id: User ID
        limit: Maximum number of scores to return

    Returns:
        List of readiness scores
    """
    scores = db.query(EnergyBudget).filter(
        EnergyBudget.user_id == user_id
    ).order_by(
        EnergyBudget.date.desc()
    ).limit(limit).all()

    return scores

@router.get("/{user_id}/readiness/trend/{days}", response_model=List[dict])
def get_readiness_trend(
    user_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get readiness score trend over specified days.

    Args:
        user_id: User ID
        days: Number of days

    Returns:
        Trend data
    """
    trend = energy_budget_calc.get_readiness_trend(db, user_id, days)
    return trend

@router.get("/{user_id}/interpretation/{rmssd}/{mean_hr}", response_model=HRVInterpretation)
def get_hrv_interpretation(
    user_id: int,
    rmssd: float,
    mean_hr: float,
    db: Session = Depends(get_db)
):
    """
    Get interpretation of HRV metrics.

    Args:
        user_id: User ID
        rmssd: RMSSD value (ms)
        mean_hr: Mean heart rate (bpm)

    Returns:
        Interpretation and recommendations
    """
    # Get active baseline
    baseline = baseline_tracker.get_active_baseline(db, user_id)
    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active baseline for interpretation"
        )

    # Calculate z-score
    try:
        z_score = baseline_tracker.calculate_hrv_z_score(rmssd, baseline)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Get interpretation
    interpretation = baseline_tracker.interpret_hrv_z_score(z_score)

    # Check population reference
    pop_check = baseline_tracker.check_population_reference(rmssd, mean_hr)
    if pop_check['has_concerns']:
        interpretation['warnings'] = pop_check['warnings']

    return interpretation
